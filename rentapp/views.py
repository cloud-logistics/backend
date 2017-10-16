#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from rest_framework import status
from util.db import query_list, save_to_db, query_list_inject
from util.geo import cal_position, get_lng_lat, get_distance, get_path_distance
from util import logger
from rest_framework.decorators import api_view
import json
import uuid
import time
import random


log = logger.get_logger(__name__)


# 可用集装箱列表
@api_view(['POST'])
def available_containers(request):
    parameters = json.loads(request.body)
    latitude = parameters['lat']
    longitude = parameters['lng']
    ret_list = []
    data = query_list('select D.deviceid,D.id as type_id,E.latitude,E.longitude from '
                      '(select A.deviceid,box_type_info.box_type_name,box_type_info.id from '
                      '(select box_info.deviceid,box_info.type from iot.box_info box_info where box_info.deviceid not in '
                      '(select deviceid from iot.monservice_containerrentinfo where rentstatus = 1)) A '
                      'left join iot.box_type_info box_type_info on A.type = box_type_info.id) D '
                      'inner join '
                      '(select B.* from (select max(timestamp) as timestamp ,deviceid from iot.sensor_data group by deviceid) A '
                      'left join iot.sensor_data B '
                      'on A.timestamp = B.timestamp and A.deviceid = B.deviceid) E '
                      'on D.deviceid = E.deviceid '
                      'where iot.fn_cal_distance(cast(iot.fn_cal_postion(E.latitude) as numeric), '
                      'cast(iot.fn_cal_postion(E.longitude) as numeric),' +
                       str(latitude) + ',' + str(longitude) + ') <= 5000')
    for i in range(len(data)):
        deviceid = data[i][0]
        type_id = data[i][1]
        latitude = data[i][2]
        longitude = data[i][3]
        ret_list.append({'id': deviceid,
                         'category': type_id,
                         'position': {'lat': cal_position(latitude),
                                      'lng': cal_position(longitude)}})
    return JsonResponse(ret_list, safe=False, status=status.HTTP_200_OK)


# 箱子种类
@api_view(['GET'])
def container_types(request):
    ret_list = []
    data = query_list('select id,box_type_name,temperature_threshold_min,temperature_threshold_max, '
                      'price,length,width,height '
                      'from iot.box_type_info where id in (3,4,5)')
    for i in range(len(data)):
        id = data[i][0]
        box_type_name = data[i][1]
        temperature_min = data[i][2]
        temperature_max = data[i][3]
        price = data[i][4]
        length = data[i][5]
        width = data[i][6]
        height = data[i][7]
        ret_list.append({'id': id,
                         'name': box_type_name,
                         'price': price,
                         'params': {
                             'temperature': {'lowThreshold': temperature_min,
                                             'highThreshold': temperature_max},
                                'length': length,
                                'width': width,
                                'height': height}})
    return JsonResponse(ret_list, safe=False, status=status.HTTP_200_OK)


# 货物种类
@api_view(['GET'])
def cargo_types(request):
    ret_list = []
    data = query_list('select id, type_name from iot.cargo_type')
    for i in range(len(data)):
        id = data[i][0]
        type_name = data[i][1]
        ret_list.append({'id': id, 'name': type_name})
    return JsonResponse(ret_list, safe=False, status=status.HTTP_200_OK)


# 保存订单
@api_view(['POST'])
def save_order(request):
    parameter = json.loads(request.body)
    user = str(request.user)
    # 起始地
    start_address = parameter['start_address']
    # 目的地
    destination_address = parameter['destination_address']
    # 租赁时间
    rent_time = parameter['rent_time']
    # 租赁云箱
    rent_box = parameter['rent_box']
    # 租赁数量
    rent_num = parameter['rent_num']
    # 租箱金额
    rent_money = parameter['rent_money']
    # 承运费用
    carry_money = parameter['carry_money']
    final_sql = ''

    try:
        available_container_list = get_available_containers(rent_box)
        if len(list(available_container_list)) < rent_num:
            return JsonResponse({'code': 'there are not enough boxes'}, safe=False, status=status.HTTP_400_BAD_REQUEST)
        trackid = str(uuid.uuid1())
        sql_1 = 'insert into iot.order_info(trackid,starttime,endtime,carrierid,start_address,destination_address,' \
                'rent_money,carry_money,create_time,owner,payment_flag) VALUES ' \
                '(\'' + trackid + '\',' + str(rent_time) + ',' + str(rent_time+1) + ',' +\
                '1,\'' + start_address + '\',\'' + destination_address + '\',' + str(rent_money) + ',' + \
                str(carry_money) + ',' + str(time.time())[0:10] + ',\'' + user + '\', 0);'
        final_sql = final_sql + sql_1
        # save_to_db(sql_1)
        for j in range(rent_num):
            sql_2 = 'insert into iot.box_order_relation(trackid, deviceid) VALUES (\'' + trackid + '\',\'' + \
                    available_container_list[j]['deviceid'] + '\');'
            # save_to_db(sql_2)
            final_sql = final_sql + sql_2
        for k in range(rent_num):
            sql_3 = 'insert into iot.monservice_containerrentinfo(deviceid, ' \
                    'starttime,endtime,carrier,type,owner,rentstatus)VALUES (' \
                    '\'' + available_container_list[k]['deviceid'] + '\',' + \
                    str(rent_time) + ',' + str(rent_time + 1) + ',' \
                    '1, ' + str(rent_box) + ',\'' + user + '\',1);'
            final_sql = final_sql + sql_3
        save_to_db(final_sql)
    except Exception, e:
        log.error('save rent order error %s' % e.message)
    return JsonResponse({'trackid': trackid}, safe=False, status=status.HTTP_200_OK)


# 我的订单
@api_view(['POST'])
def my_orders(request):
    user = str(request.user)
    ret_data = []
    data = query_list('select count(1) as container_num, order_info.trackid, '
                      'box_type_info.box_type_name, box_type_info.id, order_info.payment_flag '
                      'from iot.order_info order_info '
                      'inner join iot.box_order_relation box_order_relation '
                      'on order_info.trackid = box_order_relation.trackid '
                      'inner join iot.box_info box_info '
                      'on box_info.deviceid = box_order_relation.deviceid '
                      'inner join iot.box_type_info box_type_info '
                      'on box_info.type = box_type_info.id '
                      'where owner = \'' + user + '\' '
                      'group by box_type_info.box_type_name, box_type_info.id, '
                      'order_info.trackid,order_info.create_time, order_info.payment_flag '
                      'order by order_info.create_time desc')
    # 计算是否有告警
    for i in range(len(data)):
        trackid = data[i][1]
        payment_flag = data[i][4]
        alarm_status = 0
        if payment_flag == 1:
            alarm_data = query_list('select count(1) from iot.box_order_relation box_order_relation '
                                    'inner join iot.alarm_info alarm_info '
                                    'on box_order_relation.deviceid = alarm_info.deviceid ' 
                                    'and trackid = \'' + to_str(trackid) + '\' '
                                    'and alarm_status = 1')
            if alarm_data[0][0] > 0:
                alarm_status = 1
        item = {'container_num': data[i][0],
                'trackid': trackid,
                'box_type_name': data[i][2],
                'category': data[i][3],
                'payment_flag': payment_flag,
                'alarm_status': alarm_status}

        ret_data.append(item)
    return JsonResponse({'data': ret_data}, safe=False, status=status.HTTP_200_OK)


# 订单状态
@api_view(['POST'])
def order_status(request):
    parameter = json.loads(request.body)
    trackid = parameter['trackid']
    path_data = {}
    history_data = []
    data = query_list('select start_address,destination_address, '
                      'box_order_relation.deviceid '
                      'from  iot.order_info order_info '
                      'inner join iot.box_order_relation box_order_relation '
                      'on order_info.trackid = box_order_relation.trackid '
                      'where order_info.trackid = \'' + str(trackid) + '\''
                      'limit 1 ')
    if len(data) > 0:
        start_address = data[0][0]
        destination_address = data[0][1]
        deviceid = data[0][2]
        start_lnglat = get_lng_lat(to_str(start_address))
        destination_lnglat = get_lng_lat(to_str(destination_address))
        current_loc_data = query_list('select longitude,latitude from iot.sensor_data '
                                      'where deviceid = \'' + deviceid + '\' order by timestamp desc limit 1')
        if len(current_loc_data) > 0:
            current_lng = cal_position(current_loc_data[0][0])
            current_lat = cal_position(current_loc_data[0][1])
        else:
            current_lng = start_lnglat['lng']
            current_lat = start_lnglat['lat']
        path_data = {'start_lng': start_lnglat['lng'],
                     'start_lat': start_lnglat['lat'],
                     'destination_lng': destination_lnglat['lng'],
                     'destination_lat': destination_lnglat['lat'],
                     'current_lng': current_lng,
                     'current_lat': current_lat}
        # 获取历史流水list
        create_time_data = query_list('select create_time, payment_flag, unpacking_code, payment_time, '
                                      'rent_money, carry_money from iot.order_info where trackid = \'' + trackid + '\'')
        create_time = create_time_data[0][0]
        payment_flag = create_time_data[0][1]
        unpacking_code = create_time_data[0][2]
        payment_time = create_time_data[0][3]
        rent_money = create_time_data[0][4]
        carry_money = create_time_data[0][5]
        history_data.append({'time': to_str(create_time),
                             'description': '订单编号' + to_str(trackid)})
        history_data.append({'time': create_time + 300,
                             'description': '您的订单已开始处理'})
        history_data.append({'time': create_time + 3600,
                             'description': '云箱已出库'})
        total_distance = get_distance(start_lnglat['lat'], start_lnglat['lng'],
                                      destination_lnglat['lat'], destination_lnglat['lng'])
        start_distance = get_distance(current_lat, current_lng, start_lnglat['lat'], start_lnglat['lng'])
        end_distance = get_distance(current_lat, current_lng, destination_lnglat['lat'], destination_lnglat['lng'])

        if start_distance < total_distance and end_distance < total_distance:
            history_data.append({'time': create_time + 7300, 'description': '云箱运输中'})
        if end_distance < 5000:
            if payment_flag is not None and payment_flag == 1:
                operation = create_time + 7400
            else:
                operation = '请支付后开箱'
            history_data.append({'time': operation, 'description': '云箱已到达', 'payment_flag': 0})
        if payment_flag is not None and payment_flag == 1 and (unpacking_code is None or unpacking_code != ''):
            history_data.append({'time': payment_time, 'description': '已支付 ¥' + str(rent_money + carry_money),
                                 'payment_flag': 1})
        if unpacking_code is not None and unpacking_code != '':
            history_data.append({'time': payment_time + 7300,
                                 'description': '订单已完成 (开箱密码' + to_str(unpacking_code) + ')'})
    return JsonResponse({'history': history_data, 'path': path_data}, safe=False, status=status.HTTP_200_OK)


# 支付
@api_view(['POST'])
def order_pay(request):
    parameter = json.loads(request.body)
    trackid = parameter['trackid']
    try:
        sql_1 = 'update iot.order_info set payment_flag = 1, payment_time = ' + str(time.time())[0:10] + \
                ' where trackid = \'' + trackid + '\' and payment_flag = 0;'
        save_to_db(sql_1)
    except Exception, e:
        log.error(e.message)
    return JsonResponse({'code': 200}, safe=False, status=status.HTTP_200_OK)


# 获取开箱码
@api_view(['POST'])
def get_code(request):
    parameter = json.loads(request.body)
    trackid = parameter['trackid']
    try:
        # 生成开箱码
        unpacking_code = str(random.randint(10000, 99999))
        sql_1 = 'update iot.order_info set unpacking_code = \'' + unpacking_code + '\' ' \
                ' where trackid = \'' + trackid + '\' and payment_flag = 1;'
        sql_2 = 'update iot.monservice_containerrentinfo set rentstatus = 0 ' \
                ' where deviceid in (select deviceid from iot.box_order_relation where trackid = \'' + trackid + '\');'
        save_to_db(sql_1 + sql_2)
        data = query_list('select unpacking_code from  iot.order_info where trackid = \'' + trackid + '\'')
        if len(data) > 0:
            unpacking_code = data[0][0]
    except Exception, e:
        log.error(e.message)
    return JsonResponse({'unpacking_code': unpacking_code}, safe=False, status=status.HTTP_200_OK)


# 云箱详情总汇
@api_view(['POST'])
def status_summary(request):
    parameter = json.loads(request.body)
    trackid = parameter['trackid']
    ret_data = []
    alarm_data = query_list('select box_order_relation.deviceid,max(alarm_status) '
                            ' from iot.box_order_relation box_order_relation ' 
                            'left join iot.alarm_info alarm_info '
                            'on box_order_relation.deviceid = alarm_info.deviceid ' 
                            'and alarm_status = 1 '
                            'where box_order_relation.trackid =  \'' + to_str(trackid) + '\' '
                            'group by box_order_relation.deviceid')
    for i in range(len(alarm_data)):
        if alarm_data[i][1] is None:
            alarm_status = 0
        else:
            alarm_status = 1
        ret_data.append({'deviceid': alarm_data[i][0],
                         'alarm_status': alarm_status})
    return JsonResponse({'data': ret_data}, safe=False, status=status.HTTP_200_OK)


# 订单详情
@api_view(['POST'])
def order_detail(request):
    parameter = json.loads(request.body)
    trackid = parameter['trackid']
    ret_data = {}
    order_data = query_list('select starttime,start_address,destination_address ,box_type_name, '
                            'rent_money,carry_money,order_info.trackid,create_time '
                            'from iot.order_info order_info '
                            'inner join iot.box_order_relation box_order_relation ' 
                            'on order_info.trackid = box_order_relation.trackid '
                            'inner join iot.box_info box_info '
                            'on box_order_relation.deviceid = box_info.deviceid '
                            'inner join iot.box_type_info box_type_info '
                            'on box_info.type = box_type_info.id '
                            'where order_info.trackid = \'' + to_str(trackid) + '\' limit 1')
    if len(order_data) > 0:
        num_data = query_list('select count(1) from iot.box_order_relation where trackid = \'' + to_str(trackid) + '\'')
        rent_num = num_data[0][0]
        rent_time = order_data[0][0]
        start_address = order_data[0][1]
        destination_address = order_data[0][2]
        box_type_name = order_data[0][3]
        rent_money = order_data[0][4]
        carry_money = order_data[0][5]
        create_time = order_data[0][7]
        ret_data = {'rent_num': rent_num,
                    'rent_time': rent_time,
                    'start_address': start_address,
                    'destination_address': destination_address,
                    'box_type_name': box_type_name,
                    'rent_money': rent_money,
                    'carry_money': carry_money,
                    'create_time': create_time}
    return JsonResponse({'data': ret_data}, safe=False, status=status.HTTP_200_OK)


# 获取承运费用
@api_view(['POST'])
def get_carry_money(request):
    parameter = json.loads(request.body)
    start_address = parameter['start_address']
    destination_address = parameter['destination_address']
    distance = get_path_distance(to_str(start_address), to_str(destination_address))
    price = distance * 0.001
    return JsonResponse({'data': float('%.2f' % price)}, safe=False, status=status.HTTP_200_OK)


# 用户角色认证
@api_view(['POST'])
def app_auth(request):
    parameter = json.loads(request.body)
    username = parameter['username']
    password = parameter['password']
    try:
        data = query_list_inject("select user_name,password,role from iot.app_user "
                                 "where user_name = %s and password = %s", (username, password))
    except Exception, e:
        log.error(e.message)
        return JsonResponse({'role': 'NA'}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    if len(data) > 0:
        return JsonResponse({'role': data[0][2]}, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'role': 'NA'}, safe=False, status=status.HTTP_400_BAD_REQUEST)


# 查询可用租用的箱子
def get_available_containers(id):
    ret_list = []
    sql = 'select A.deviceid, box_type_info.id as type_id from ' \
          '(select box_info.deviceid,box_info.type from iot.box_info box_info where box_info.deviceid not in ' \
          '(select deviceid from iot.monservice_containerrentinfo where rentstatus = 1)) A ' \
          'left join iot.box_type_info box_type_info on A.type = box_type_info.id where box_type_info.id = ' + str(id)
    data = query_list(sql)
    for i in range(len(data)):
        ret_list.append({'deviceid': data[i][0], 'type_id': data[i][1]})
    return ret_list


# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value
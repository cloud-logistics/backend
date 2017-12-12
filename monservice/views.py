#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import traceback
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import settings
from util.db import query_list, save_to_db
from util.geo import cal_position, get_lng_lat, get_position_name
from util import logger
from util.cid import generate_cid, generate_cid_new
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
import urllib
import urllib2
import json
import random
from monservice.serializers import *
from monservice.models import *
from math import ceil


log = logger.get_logger('monservice.view.py')
NOT_APPLICABLE = 'NA'
ZERO = 0
STATUS_NORMAL = '正常'
STATUS_ABNORMAL = '异常'
UNAVAILABLE = '不可用'
AVAILABLE = '可用'
REDIS_MAP_KEY = 'gpsmap'


@csrf_exempt
def containers_overview(request):
    try:
        container_info_list = []
        data = query_list('select box_info.deviceid,box_type_info.box_type_name, '
                          'C.latitude,C.longitude '
                          'from iot.monservice_boxinfo box_info '
                          'left join iot.monservice_boxtypeinfo box_type_info '
                          'on box_info.type_id = box_type_info.id ' 
                          'left join '
                          '(select B.* from (select max(timestamp) as timestamp ,deviceid ' 
                          'from iot.monservice_sensordata group by deviceid) A ' 
                          'left join iot.monservice_sensordata B '
                          'on A.timestamp = B.timestamp and A.deviceid = B.deviceid) C '
                          'on box_info.deviceid = C.deviceid '
                          'order by deviceid asc')
        for item in data:
            container_dict = {}
            container_dict['title'] = item[0]
            lng = cal_position((item[3], '0')[item[3] is None])
            lat = cal_position((item[2], '0')[item[2] is None])
            gps_dic = {'lng': float(lng), 'lat': float(lat)}
            container_dict['position'] = gps_dic
            # container_dict['detail'] = gps_info_trans("%s,%s" % (gps_dic['lat'], gps_dic['lng']))
            container_info_list.append(container_dict)
        return JsonResponse(container_info_list, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('containers_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 实时报文
@csrf_exempt
def realtime_message(request):
    try:
        id = json.loads(request.body)['containerId']
    except Exception, e:
        id = NOT_APPLICABLE
        log.error(e.message)

    count = BoxInfo.objects.filter(deviceid=id).count()
    if count == 0:
        response_msg = {'status': 'NoDataFound', 'msg': u'箱子不存在！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

    # 获取承运方
    carrier_name = 'NA'

    # 获取云箱型号
    box_type_data = query_list('select box_type_info.box_type_name from iot.monservice_boxinfo box_info '
                               'left join iot.monservice_boxtypeinfo box_type_info on box_info.type_id = box_type_info.id '
                               'where box_info.deviceid = \'' + id + '\' group by box_type_info.box_type_name')

    if len(box_type_data) > 0:
        box_type = box_type_data[0][0]
    else:
        box_type = NOT_APPLICABLE

    # 获取传感器数据
    sensor_data = query_list('select temperature,humidity,longitude,latitude,speed,collide,light,timestamp '
                             'from iot.monservice_sensordata where deviceid = \'' + id + '\' order by timestamp desc limit 1')
    if len(sensor_data) > 0:
        temperature = sensor_data[0][0]
        humidity = sensor_data[0][1]
        longitude = cal_position(sensor_data[0][2])
        latitude = cal_position(sensor_data[0][3])
        speed = sensor_data[0][4]
        collide = sensor_data[0][5]
        light = sensor_data[0][6]  # 表示电量
        num_of_door_open = 5

    else:
        temperature = ZERO
        humidity = ZERO
        longitude = ZERO
        latitude = ZERO
        speed = ZERO
        collide = ZERO
        light = ZERO   # 表示电量
        num_of_door_open = ZERO

    # 获取箱子阈值
    threshold_data = query_list('select temperature_threshold_max,temperature_threshold_min,'
                                'humidity_threshold_max,humidity_threshold_min,'
                                'collision_threshold_max,collision_threshold_min,'
                                'battery_threshold_max,battery_threshold_min,'
                                'operation_threshold_max,operation_threshold_min ' \
                                'from iot.monservice_boxinfo box_info ' \
                                'INNER join iot.monservice_boxtypeinfo box_type_info on box_info.type_id = box_type_info.id '
                                'where deviceid = \'' + id + '\'')

    if len(threshold_data) > 0:
        temperature_threshold_max = threshold_data[0][0]
        temperature_threshold_min = threshold_data[0][1]
        humidity_threshold_max = threshold_data[0][2]
        humidity_threshold_min = threshold_data[0][3]
        collision_threshold_max = threshold_data[0][4]
        collision_threshold_min = threshold_data[0][5]
        battery_threshold_max = threshold_data[0][6]
        battery_threshold_min = threshold_data[0][7]
        operation_threshold_max = threshold_data[0][8]
        operation_threshold_min = threshold_data[0][9]

    else:
        temperature_threshold_max = ZERO
        temperature_threshold_min = ZERO
        humidity_threshold_max = ZERO
        humidity_threshold_min = ZERO
        collision_threshold_max = ZERO
        collision_threshold_min = ZERO
        battery_threshold_max = ZERO
        battery_threshold_min = ZERO
        operation_threshold_max = ZERO
        operation_threshold_min = ZERO

    # 计算箱子在运还是停靠
    try:
        box = BoxInfo.objects.get(deviceid=id)
        shipping_status = (AVAILABLE, UNAVAILABLE)[box.siteinfo_id is None]
    except Exception, e:
        shipping_status = UNAVAILABLE
        log.error(e.message)

    # 计算温度是否在正常范围
    if float(temperature_threshold_min) <= float(temperature) <= float(temperature_threshold_max):
        temperature_status = STATUS_NORMAL
    else:
        temperature_status = STATUS_ABNORMAL

    # 计算湿度是否在正常范围
    if humidity_threshold_min <= float(humidity) <= humidity_threshold_max:
        humidity_status = STATUS_NORMAL
    else:
        humidity_status = STATUS_ABNORMAL

    # 计算电量是否咋正常范围
    battery = light           # 后续需要修改为真实值, 目前使用light字段表示电量
    if float(battery_threshold_min) <= float(battery) <= float(battery_threshold_max):
        battery_status = STATUS_NORMAL
    else:
        battery_status = STATUS_ABNORMAL

    # 计算碰撞次数是否咋正常范围
    if collision_threshold_min <= int(collide) <= collision_threshold_max:
        collide_status = STATUS_NORMAL
    else:
        collide_status = STATUS_ABNORMAL

    # 计算开门次数是否在正常范围
    if operation_threshold_min <= int(num_of_door_open) <= operation_threshold_max:
        door_open_status = STATUS_NORMAL
    else:
        door_open_status = STATUS_ABNORMAL

    ret_data = {'containerId': id,
                'containerType': box_type,
                'currentStatus': shipping_status,
                'carrier': carrier_name, 'position': {'lng': longitude, 'lat': latitude},
                'locationName': gps_info_trans("%s,%s" % (latitude, longitude)),
                'speed': float(speed),
                'temperature': {'value': float(temperature), 'status': temperature_status},
                'humidity': {'value': float(humidity), 'status': humidity_status},
                'battery': {'value': float(battery), 'status': battery_status},
                'boxStatus': {'num_of_collide': {'value': int(collide), 'status': collide_status},
                              'num_of_door_open': {'value': int(num_of_door_open), 'status': door_open_status}}}
    return JsonResponse(ret_data, safe=True, status=status.HTTP_200_OK)


# 实时位置
@csrf_exempt
def realtime_position(request):
    try:
        id = json.loads(request.body)['containerId']
    except Exception, e:
        id = NOT_APPLICABLE
        log.error(e.message)

    count = BoxInfo.objects.filter(deviceid=id).count()
    if count == 0:
        response_msg = {'status': 'NoDataFound', 'msg': u'箱子不存在！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

    cur_data = query_list('select latitude,longitude from iot.monservice_sensordata '
                          'where deviceid = \'' + id + '\' '
                          'and latitude <> \'0\' and longitude <> \'0\' order by timestamp desc limit 1')
    if len(cur_data) > 0:
        cur_latitude = cal_position(cur_data[0][0])
        cur_longitude = cal_position(cur_data[0][1])
    else:
        cur_latitude = ZERO
        cur_longitude = ZERO
    cur_location_name = gps_info_trans("%s,%s" % (cur_latitude, cur_longitude))
    ret_data = {'currentPosition': {'lng': cur_longitude, 'lat': cur_latitude},
                'currentLocationName': cur_location_name}

    return JsonResponse(ret_data, safe=True, status=status.HTTP_200_OK)


# 报警监控
@csrf_exempt
@api_view(['GET'])
def alarm_monitor(request):
    container_id = request.GET.get('container_id')
    alert_type_id = request.GET.get('alert_type_id')

    deviceid = (container_id, '')[container_id == 'all']
    sql = 'select alarm_info.deviceid,alert_level_info.level,alarm_info.timestamp, ' + \
          'alert_code_info.description,alarm_info.code,alarm_info.status, ' + \
          'alarm_info.longitude,alarm_info.latitude,' + \
          'alarm_info.speed,alarm_info.temperature,alarm_info.humidity,' + \
          'alarm_info.num_of_collide,alarm_info.num_of_door_open,' + \
          'alarm_info.battery,alarm_info.robert_operation_status,' + \
          'alarm_info.endpointid, alarm_info.id ' + \
          'from iot.monservice_alarminfo alarm_info ' + \
          'left join iot.monservice_alertlevelinfo alert_level_info on alarm_info.level = alert_level_info.id ' + \
          'left join iot.monservice_alertcodeinfo alert_code_info on alarm_info.code = alert_code_info.errcode ' + \
          'where alarm_info.alarm_status = 1 ' + \
          'and (alert_code_info.id = ' + str(alert_type_id) + ' or ' + str(alert_type_id) + ' = 0) ' + \
          ' and (alarm_info.deviceid like \'%' + to_str(deviceid) + '%\' or \'' + deviceid + '\'= \'\') ' \
          ' order by timestamp desc'
    data = query_list(sql)
    ret_data = []

    for record in data:
        deviceid = record[0]
        timestamp = record[2] * 1000        # 前端显示需要精确到毫秒
        error_description = record[3]
        error_code = record[4]
        ship_status = record[5]
        longitude = cal_position(record[6])
        latitude = cal_position(record[7])
        speed = record[8]
        temperature = record[9]
        humidity = record[10]
        num_of_collide = record[11]
        num_of_door_open = record[12]
        battery = record[13]
        robert_operation_status = record[14]
        endpointid = record[15]
        location_name = gps_info_trans("%s,%s" % (latitude, longitude)).decode("utf-8")
        ret_data.append({'timestamp': timestamp, 'deviceid': deviceid,
                         'level': 1, 'status': u'', 'carrier': 1, 'alarm_status': 1,
                         'error_description': error_description, 'code': error_code,
                         'longitude': longitude, 'latitude': latitude,
                         'speed': speed, 'temperature': temperature,
                         'humidity': humidity,
                         'num_of_collide': num_of_collide,
                         'num_of_door_open': num_of_door_open,
                         'battery':battery, 'robert_operation_status': robert_operation_status,
                         'location_name': location_name, "endpointid": endpointid})
    pagination_class = settings.api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    page = paginator.paginate_queryset(ret_data, request)
    ret_list = RetAlarmSerializer(page, many=True)
    return paginator.get_paginated_response(ret_list.data, 'OK', 'query alarm success')


# 基础信息查询
@csrf_exempt
@api_view(['GET'])
def basic_info(request):
    container_id = request.GET.get('container_id')
    container_type = request.GET.get('container_type')
    factory = request.GET.get('factory')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    date_condition = ''
    if start_time == '0' and end_time != '0':
        date_condition = ' and date_of_production < \'' + str(end_time) + '\''
    elif start_time != '0' and end_time == '0':
        date_condition = ' and date_of_production >= \'' + str(start_time) + '\''
    elif start_time != '0' and end_time != '0':
        date_condition = ' and date_of_production >= \'' + str(start_time) + \
                         '\' and date_of_production < \'' + str(end_time) + '\''
    elif start_time == '0' and end_time == '0':
        date_condition = ''

    query_sql = 'select box_info.deviceid,box_info.tid, box_type_info.box_type_name, produce_area_info.address, ' \
                'manufacturer_info.name, date_of_production, battery_info.battery_detail,box_type_info.id,' \
                'produce_area_info.id,manufacturer_info.id,battery_info.id,hardware.hardware_detail,hardware.id ' \
                'from iot.monservice_boxinfo box_info ' \
                'left join iot.monservice_boxtypeinfo box_type_info on box_info.type_id = box_type_info.id ' \
                'left join iot.monservice_producearea produce_area_info on box_info.produce_area_id = produce_area_info.id ' \
                'left join iot.monservice_manufacturer manufacturer_info on box_info.manufacturer_id = manufacturer_info.id ' \
                'left join iot.monservice_battery battery_info on battery_info.id = box_info.battery_id ' \
                'left join iot.monservice_hardware hardware on hardware.id = box_info.hardware_id ' \
                'where (deviceid like \'%' + str(container_id) + '%\' or \'' + str(container_id) +  \
                '\' = \'all\') ' + \
                ' and (box_type_info.id = ' + str(container_type) + ' or ' + str(container_type) + ' = 0 ) ' + \
                ' and  (manufacturer_info.id = ' + str(factory) + ' or ' + str(factory) + ' = 0 ) ' + \
                date_condition + \
                ' group by box_info.deviceid, box_type_name, produce_area_info.address, manufacturer_info.name, ' \
                'date_of_production, battery_detail, box_type_info.id,produce_area_info.id,manufacturer_info.id,' \
                'battery_info.id,hardware.hardware_detail,hardware.id '
    data = query_list(query_sql)
    data_list = []
    for item in data:
        dicitem = {}
        dicitem['deviceid'] = item[0]
        dicitem['tid'] = item[1]
        dicitem['box_type_name'] = item[2]
        dicitem['produce_area'] = item[3]
        dicitem['manufacturer'] = item[4]
        dicitem['date_of_production'] = item[5]
        dicitem['battery_detail'] = item[6]
        dicitem['box_type_id'] = item[7]
        dicitem['produce_area_id'] = item[8]
        dicitem['manufacturer_id'] = item[9]
        dicitem['battery_id'] = item[10]
        dicitem['hardware_detail'] = item[11]
        dicitem['hardware_id'] = item[12]
        data_list.append(dicitem)

    pagination_class = settings.api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    page = paginator.paginate_queryset(data_list, request)
    ret_data = BoxBasicInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_data.data, 'OK', 'query alarm success')


@csrf_exempt
def history_path(request):
    param = request.body
    container_dic_list = []
    final_response = {}
    if param:
        try:
            param_dic = json.loads(param)
            if param_dic['containerId'] and param_dic['startTime'] and param_dic['endTime']:
                request_starttime = get_utc(param_dic['startTime'])
                request_endtime = get_utc(param_dic['endTime'])
                query_template = '''select srcid, dstid, starttime, endtime
                        from iot.monservice_orderinfo where iot.monservice_orderinfo.trackid
                        in (select trackid from iot.monservice_boxorderrelation
                        where iot.box_order_relation.deviceid = '%s')''' % param_dic['containerId']
                order_info_query_list = query_list(query_template)
                site_info_query_list = query_list('select id, latitude, longitude from iot.monservice_siteinfo')
                site_info_dic = {}
                '''
                site info dic
                dic ['id'] = {'lat':12, 'lng':120}
                '''
                log.info("site_info_query_list:%s" % site_info_query_list)
                for item in site_info_query_list:
                    gpsdic = {}
                    # string to float type
                    gpsdic['lat'] = float(item[1])
                    gpsdic['lng'] = float(item[2])
                    site_info_dic[item[0]] = gpsdic
                # contract final response
                log.info("order_info_query_list:%s" % order_info_query_list)
                log.info("request_starttime:%s" % request_starttime)
                log.info("request_endtime:%s" % request_endtime)
                for item in order_info_query_list:
                    if len(request_starttime) > 10:
                        req_starttime_int = int(request_starttime) / 1000
                    else:
                        req_starttime_int = int(request_starttime)
                    if len(request_endtime) > 10:
                        req_endtime_int = int(request_endtime) / 1000
                    else:
                        req_endtime_int = int(request_endtime)
                    if req_starttime_int <= int(item[2]) and req_endtime_int >= int(item[3]):
                        start_dic = {}
                        start_dic['time'] = item[2]
                        if item[0] in site_info_dic.keys():
                            start_dic['position'] = site_info_dic[item[0]]
                            start_gps_info = "%s,%s" % (start_dic['position']['lat'], start_dic['position']['lng'])
                            log.info("start_position gpsinfo is %s" % start_gps_info)
                            start_dic['locationName'] = gps_info_trans(start_gps_info)
                        end_dic = {}
                        end_dic['time'] = item[3]
                        if item[1] in site_info_dic.keys():
                            end_dic['position'] = site_info_dic[item[1]]
                            end_gps_info = "%s,%s" % (end_dic['position']['lat'], end_dic['position']['lng'])
                            log.info("end_position gpsinfo is %s" % end_gps_info)
                            end_dic['locationName'] = gps_info_trans(end_gps_info)
                        container_dic = {}
                        container_dic['containerId'] = param_dic['containerId']
                        container_dic['start'] = start_dic
                        container_dic['end'] = end_dic
                        container_dic_list.append(container_dic)
                final_response['containerhistory'] = container_dic_list
                log.info("final_response:%s" % final_response)
        except Exception, e:
            log.error(e)
        finally:
            return JsonResponse(final_response, safe=True, status=status.HTTP_200_OK)
    else:
        return JsonResponse(final_response, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 云箱历史轨迹
@csrf_exempt
@api_view(['GET'])
def box_history_path(request):
    try:
        deviceid = request.GET.get('containerId')

        count = BoxInfo.objects.filter(deviceid=deviceid).count()
        if count == 0:
            response_msg = {'status': 'NoDataFound', 'msg': u'箱子不存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        locations = SensorData.objects.filter(deviceid=deviceid, timestamp__gte=start_time, timestamp__lte=end_time).exclude(longitude='0', latitude='0')
        total_num = len(locations)
        if total_num > 0:
            span_num = 20
            step = int(ceil(total_num/float(span_num)))
            locations = locations[::step]
        locations_ser = SensorPathDataSerializer(locations, many=True)
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get history path success', 'path': locations_ser.data}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 云箱状态汇总
@api_view(['GET'])
def status_summary(request):
    container_id = request.GET.get('container_id')
    container_type = request.GET.get('container_type')
    location_id = request.GET.get('location_id')
    id = container_id

    sql = 'select box_info.deviceid,C.timestamp,C.longitude,C.latitude,' \
          'C.speed,C.temperature,C.humidity,C.collide,C.light,box_info.ava_flag ' \
          'from iot.monservice_boxinfo box_info ' \

    sql = sql + ' left join ( select B.* from ' \
                '(select max(timestamp) as timestamp ,deviceid from iot.monservice_sensordata '

    if id is not None and id != 'all':
        sql = sql + 'where deviceid like \'%' + id + '%\' '

    sql = sql + 'group by deviceid) A left join iot.monservice_sensordata B ' \
                'on A.timestamp = B.timestamp and A.deviceid = B.deviceid '

    if id is not None and id != 'all':
        sql = sql + 'where B.deviceid like \'%' + id + '%\''

    sql = sql + ') C on C.deviceid=box_info.deviceid where ' \
                '(box_info.type_id = ' + str(container_type) + ' or ' + container_type + ' = 0)' \
                ' and (siteinfo_id = ' + location_id + ' or ' + location_id + ' = 0)'
    if id is not None and id != 'all':
        sql = sql + ' and box_info.deviceid like \'%' + id + '%\' '
    sql = sql + ' group by box_info.deviceid,C.timestamp, ' \
                'C.longitude,C.latitude,C.speed,C.temperature,C.humidity,C.collide,C.light'
    data = query_list(sql)

    ret_data = []

    for item in data:
        deviceid = item[0]
        timestamp = item[1]
        longitude = cal_position((item[2], '0')[item[2] is None])
        latitude = cal_position((item[3], '0')[item[3] is None])
        speed = round(float((item[4], 0)[item[4] is None]), 2)
        temperature = round(float((item[5], 0)[item[5] is None]), 2)
        humidity = round(float((item[6], 0)[item[6] is None]), 2)
        collide = int((item[7], 0)[item[7] is None])
        light = float((item[8], 0)[item[8] is None])
        available_status = (item[9], u'N')[item[9] is None]
        num_of_door_open = 5

        if available_status == u'Y':
            available_status= u'可用'
        else:
            available_status = u'不可用'

        location_name = gps_info_trans("%s,%s" % (latitude, longitude)).decode("utf-8")

        element = {'deviceid': deviceid, 'longitude': longitude, 'latitude': latitude, 'location_name': location_name,
                   'speed': speed, 'temperature': temperature, 'humidity': humidity, 'collide': collide,
                   'num_of_door_open': num_of_door_open, 'robot_operation_status': u'装箱', 'battery': light,
                   'available_status': available_status}
        ret_data.append(element)
    pagination_class = settings.api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    page = paginator.paginate_queryset(ret_data, request)
    ret_list = BoxSummarySerializer(page, many=True)
    return paginator.get_paginated_response(ret_list.data, 'OK', 'query alarm success')


def new_containerid(category, date_of_production):
    sql = '''select nextval('iot.monservice_box_id_seq') from iot.monservice_box_id_seq'''
    id_query = query_list(sql)
    sn = id_query[0][0]
    cid = generate_cid_new(sn, category, date_of_production)
    return cid


# 云箱基础信息录入
@csrf_exempt
@api_view(['POST'])
def basic_info_config(request):
    try:
        data = json.loads(request.body)
        rfid = to_str(data['rfid'])                             # RFID

        boxes = BoxInfo.objects.filter(tid=rfid)
        if len(boxes) > 0:
            response_msg = {'status': 'ERROR', 'msg': '云箱RFID已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        date_of_production = to_str(data['manufactureTime'])    # 生产日期
        battery_info = data['batteryInfo']                      # 电源信息
        bat = Battery.objects.get(id=battery_info)
        manufacturer = data['factory']                          # 生产厂家
        man = Manufacturer.objects.get(id=manufacturer)
        produce_area = data['factoryLocation']                  # 生产地点
        pro = ProduceArea.objects.get(id=produce_area)
        hardware_info = data['hardwareInfo']                    # 智能硬件信息
        hard = Hardware.objects.get(id=hardware_info)
        category = data['containerType']

        container_id = new_containerid(str(category), date_of_production)           # 生成云箱id

        box_type = BoxTypeInfo.objects.get(id=category)
        box = BoxInfo(deviceid=container_id, type=box_type, date_of_production=date_of_production, manufacturer=man,
                      produce_area=pro, hardware=hard, battery=bat, carrier=1, tid=rfid, ava_flag='N')
        box.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'录入云箱基础信息成功！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 根据云箱RFID获取ContainerID
@csrf_exempt
@api_view(['GET'])
def get_containerid_by_rfid(request, rfid):
    try:
        log.debug(request.get_full_path())

        box = BoxInfo.objects.get(tid=rfid)

        site_id = request.GET.get('siteID')
        if site_id is None:
            response_msg = {'result': 'False', 'code': '999999', 'msg': 'Site ID is None.'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        if box.siteinfo_id is None and box.ava_flag == 'N':
            box.siteinfo_id = site_id
            box.ava_flag = 'Y'
            stock = SiteBoxStock.objects.get(site_id=site_id, box_type=box.type)
            stock.ava_num += 1

            ts = str(time.time())[0:10]
            op_type = '1'  # 操作类型：1表示入仓，0表示出仓
            history = SiteHistory(timestamp=ts, site_id=site_id, box_id=box.deviceid, op_type=op_type)

            stock.save()
            box.save()
            history.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success', 'containerID': box.deviceid}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)



# 修改云箱基础信息
@csrf_exempt
@api_view(['PUT'])
def modify_basic_info(request):
    try:
        data = json.loads(request.body)
        container_id = to_str(data['containerId'])  # 云箱id
        box = BoxInfo.objects.get(deviceid=container_id)
        rfid = to_str(data['rfid'])  # RFID

        boxes = BoxInfo.objects.filter(tid=rfid).exclude(deviceid=container_id)
        if boxes.count() > 0:
            response_msg = {'status': 'ERROR', 'msg': '云箱RFID已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        date_of_production = to_str(data['manufactureTime'])  # 生产日期
        battery_info = data['batteryInfo']  # 电源信息
        manufacturer = data['factory']  # 生产厂家
        produce_area = data['factoryLocation']  # 生产地点
        hardware_info = data['hardwareInfo']  # 智能硬件信息
        category = data['containerType']

        box.type = BoxTypeInfo.objects.get(id=category)
        box.date_of_production = date_of_production
        box.manufacturer = Manufacturer.objects.get(id=manufacturer)
        box.produce_area = ProduceArea.objects.get(id=produce_area)
        box.hardware = Hardware.objects.get(id=hardware_info)
        box.battery = Battery.objects.get(id=battery_info)
        box.tid = rfid

        box.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'修改云箱基础信息成功！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 删除云箱基础信息
@csrf_exempt
@api_view(['DELETE'])
def remove_basic_info(request, id):
    try:
        container_id = str(id)
        box = BoxInfo.objects.get(deviceid=container_id)
        if box.siteinfo_id is None:
            if box.ava_flag == 'Y':
                response_msg = {'status': 'ERROR', 'msg': u'该箱子在运输中，无法删除！'}
                return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                BoxInfo.objects.get(deviceid=container_id).delete()
        else:
            BoxInfo.objects.get(deviceid=container_id).delete()
            stock = SiteBoxStock.objects.get(site_id=box.siteinfo_id, box_type=box.type)
            stock.ava_num -= 1
            stock.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'删除云箱基础信息成功！'}
        return JsonResponse(response_msg, safe=False, status=status.HTTP_200_OK)


# 根据堆场ID获取堆场内的云箱
@csrf_exempt
@api_view(['GET'])
def get_site_boxes(request, id):
    try:
        site_info = SiteInfo.objects.get(id=id)
    except SiteInfo.DoesNotExist:
        return JsonResponse({'code': '9999', 'msg': 'error'}, safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取各种类型箱子的可用个数
    box_counts = []
    type_list = BoxTypeInfo.objects.all()
    for _type in type_list:
        box_num = BoxInfo.objects.filter(siteinfo=site_info, type=_type).count()
        box_counts.append({'box_type': BoxTypeInfoSerializer(_type).data, 'box_num': box_num})
    return JsonResponse(
        {'site_info': SiteInfoSerializer(site_info).data, 'box_counts': box_counts},
        safe=True,
        status=status.HTTP_200_OK)


@csrf_exempt
def options_to_show(request):
    final_response = {}
    req_param_str_utf8 = to_str(request.body)
    req_param = json.loads(req_param_str_utf8)
    try:
        options_type = req_param['optionsType']
    except KeyError, e:
        log.error(e.message)
        options_type = 1

    if req_param:
        if req_param['requiredOptions']:
            for item in req_param['requiredOptions']:
                if item == 'alertLevel':
                    alert_level_list = query_list(('select 0 as id, \'全部\' as level union ', '')[options_type != 1] +
                                                  'select id,level from '
                                                  'iot.monservice_alertlevelinfo order by id asc')
                    final_response['alertLevel'] = strip_tuple(alert_level_list)
                if item == 'alertCode':
                    alert_code_list = query_list(('select 0 as id, \'全部\' as errcode union ', '')[options_type != 1] +
                                                 'select id, (CAST (errcode AS text)) '
                                                 'from iot.monservice_alertcodeinfo order by id asc')
                    final_response['alertCode'] = strip_tuple(alert_code_list)
                if item == 'alertType':
                    alert_type_list = query_list(('select 0 as id, \'全部\' as type union ', '')[options_type != 1] +
                                                 'select id, description as type '
                                                 'from iot.monservice_alertcodeinfo order by id asc')
                    final_response['alertType'] = strip_tuple(alert_type_list)
                if item == 'containerType':
                    container_type_list = query_list(('select 0 as id, \'全部\' as box_type_name union ', '')
                                                     [options_type != 1] +
                                                     'select id,box_type_name '
                                                     'from iot.monservice_boxtypeinfo order by id asc')
                    final_response['containerType'] = strip_tuple(container_type_list)
                if item == 'currentStatus':
                    status_list = []
                    # status_list.append(to_str(IN_TRANSPORT))
                    # status_list.append(to_str(ANCHORED))
                    final_response['currentStatus'] = status_list
                if item == 'location':
                    location_list = query_list(('select 0 as id, \'全部\' as location union ', '')[options_type != 1] +
                                               'select id,location '
                                               'from iot.monservice_siteinfo order by id asc')
                    final_response['location'] = strip_tuple(location_list)
                if item == 'factory':
                    factory_list = query_list(('select 0 as id, \'全部\' as name union ', '')[options_type != 1] +
                                              'select id,name '
                                              'from iot.monservice_manufacturer order by id asc')
                    final_response['factory'] = strip_tuple(factory_list)
                if item == 'factoryLocation':
                    location_list = query_list(('select 0 as id, \'全部\' as address union ', '')[options_type != 1] +
                                               'select id,address '
                                               'from iot.monservice_producearea order by id asc')
                    final_response['factoryLocation'] = strip_tuple(location_list)
                if item == 'batteryInfo':
                    batteryinfo_list = query_list(('select 0 as id, \'全部\' as battery_detail union ', '')
                                                  [options_type != 1] +
                                                  'select id,battery_detail '
                                                  'from iot.monservice_battery order by id asc')
                    final_response['batteryInfo'] = strip_tuple(batteryinfo_list)
                if item == 'maintenanceLocation':
                    final_response['maintenanceLocation'] = strip_tuple([])
                if item == 'intervalTime':
                    interval_time_list = query_list(('select 0 as id, \'全部\' as interval_time_min union ', '')
                                                    [options_type != 1] +
                                                    'select id,(CAST (interval_time_min AS text)) '
                                                    'from iot.monservice_intervaltimeinfo order by id asc')
                    # interval time type is integer
                    final_response['intervalTime'] = strip_tuple(interval_time_list)
                if item == 'hardwareInfo':
                    hardware_info_list = query_list(('select 0 as id, \'全部\' as hardware_detail union ', '')
                                                    [options_type != 1] +
                                                    'select id,hardware_detail '
                                                    'from iot.monservice_hardware order by id asc')
                    final_response['hardwareInfo'] = strip_tuple(hardware_info_list)
            log.debug(json.dumps(final_response))
            return JsonResponse(final_response, safe=True, status=status.HTTP_200_OK)
        else:
            return JsonResponse(req_param, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(req_param, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def security_config(request):
    final_response = {}
    req_param_str_utf8 = to_str(request.body)
    req_param = json.loads(req_param_str_utf8)
    append_sql = lambda x,y : x + y + ','
    final_append_sql = lambda x, y: x + y
    sql_template = '''update iot.monservice_boxtypeinfo set %s'''
    column_string = ''
    if req_param:
        container_type_list = query_list('select id from iot.monservice_boxtypeinfo')
        final_type_list = strip_tuple(container_type_list, 0)
        log.info("safe_param_to_set: final_type_list = %s" % final_type_list)
        log.info("safe_param_to_set: containerType = %s" % req_param['containerType'])
        if int(req_param['containerType']) in final_type_list:
            insert_key_list = req_param.keys()
            if 'intervalTime' in insert_key_list:
                # column_string = column_string + 'intervalTime' + ','
                interval_value_list = query_list("select interval_time_min from iot.monservice_intervaltimeinfo where id = '%s'"
                                        % req_param['intervalTime'])
                log.info("interval_value_list = %s" % interval_value_list)
                interval_time_list = strip_tuple(interval_value_list, 0)
                column_string = append_sql(column_string, "interval_time=%s" % interval_time_list[0])
            if 'temperature' in insert_key_list:
                if 'min' in req_param['temperature'].keys():
                    column_string = append_sql(column_string,
                                               "temperature_threshold_min=%s" % req_param['temperature']['min'])
                if 'max' in req_param['temperature'].keys():
                    column_string = append_sql(column_string,
                                               "temperature_threshold_max=%s" % req_param['temperature']['max'])
            if 'humidity' in insert_key_list:
                if 'min' in req_param['humidity'].keys():
                    column_string = append_sql(column_string,
                                               "humidity_threshold_min=%s" % req_param['humidity']['min'])
                if 'max' in req_param['humidity'].keys():
                    column_string = append_sql(column_string,
                                               "humidity_threshold_max=%s" % req_param['humidity']['max'])
            if 'collision' in insert_key_list:
                if 'min' in req_param['collision'].keys():
                    column_string = append_sql(column_string,
                                               "collision_threshold_min=%s" % req_param['collision']['min'])
                if 'max' in req_param['collision'].keys():
                    column_string = append_sql(column_string,
                                               "collision_threshold_max=%s" % req_param['collision']['max'])
            if 'battery' in insert_key_list:
                if 'min' in req_param['battery'].keys():
                    column_string = append_sql(column_string,
                                               "battery_threshold_min=%s" % req_param['battery']['min'])
                if 'max' in req_param['battery'].keys():
                    column_string = append_sql(column_string,
                                               "battery_threshold_max=%s" % req_param['battery']['max'])
            if 'operation' in insert_key_list:
                if 'min' in req_param['operation'].keys():
                    column_string = append_sql(column_string,
                                               "operation_threshold_min=%s" % req_param['operation']['min'])
                if 'max' in req_param['operation'].keys():
                    column_string = final_append_sql(column_string,
                                               "operation_threshold_max=%s" % req_param['operation']['max'])
            log.info(sql_template % column_string)
            try:
                save_to_db(sql_template % column_string)
            except Exception, e:
                log.error(e)
                return JsonResponse(final_response, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return JsonResponse(final_response, safe=True, status=status.HTTP_200_OK)
        else:
            return JsonResponse(req_param, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(req_param, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login(request):
    ret_dict = {}
    req_param = JSONParser().parse(request)
    try:
        username = req_param['username']
    except Exception:
        return JsonResponse({'msg': '请输入账号'}, safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        password = req_param['password']
    except Exception:
        return JsonResponse({'msg': '请输入密码'}, safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        timestamp = req_param['timestamp']
    except Exception:
        return JsonResponse({'msg': '请求异常'}, safe=True, status=status.HTTP_400_BAD_REQUEST)

    if abs(int(str(time.time())[0:10]) - timestamp) < 60 * 5:
        sql = 'select user_token from iot.monservice_sysuser where user_name = \'' + username + \
              '\' and md5(md5(user_password) || CAST(' + str(timestamp) + ' AS VARCHAR)) = \'' +\
              password + '\''
        user_list = query_list(sql)
        if len(user_list) > 0:
            ret_dict['role'] = 'carrier'
            ret_dict['token'] = user_list[0][0]
            request.session[user_list[0][0]] = user_list[0][0]
            return JsonResponse(ret_dict, safe=True, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'msg': '账号或密码错误'}, safe=True, status=status.HTTP_403_FORBIDDEN)
    else:
        log.info('auth interface timestamp is invade')
        return JsonResponse({'msg': '账号或密码错误'}, safe=True, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        del request.session[token]
        return JsonResponse({'msg': '退出成功'}, safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        return JsonResponse({'msg': '退出错误'}, safe=True, status=status.HTTP_400_BAD_REQUEST)


# 向终端发送command
# @authentication_classes((SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication))
# @permission_classes((IsAuthenticated,))
@api_view(['POST'])
def send_command(request):
    action = json.loads(request.body)['action']
    id = json.loads(request.body)['endpointId']
    conn = redis.Redis(host="127.0.0.1", port=6379, db=0)
    command = "{\"service\":\"command\",\"action\": \"" + action + "\",\"result\":\"\",\"id\":\"" + id + "\"}"
    conn.publish("commandChannel", command)

    conn.save()
    return JsonResponse({"code": "200"}, safe=True, status=status.HTTP_200_OK)


# 实时报文温度、湿度曲线
# @authentication_classes((SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication))
# @permission_classes((IsAuthenticated,))
@api_view(['POST'])
def indicator_history(request):
    try:
        id = json.loads(request.body)['containerId']
    except Exception, e:
        id= ""

    count = BoxInfo.objects.filter(deviceid=id).count()
    if count == 0:
        response_msg = {'status': 'NoDataFound', 'msg': u'箱子不存在！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

    try:
        indicator = json.loads(request.body)['requiredParam']
    except Exception, e:
        indicator = "temperature"
    try:
        days = json.loads(request.body)['days']
    except Exception, e:
        days = 1
    try:
        end_time_str = str(time.strftime('%Y-%m-%d %H', time.localtime(int(time.time())))) + ':00:00'
        end_time = int(time.mktime(time.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')))
        start_time = end_time - 3600 * 24 * days

        data_dic = {}
        value_arr = []

        if indicator != 'battery':
            data_list = query_list('SELECT * FROM iot.fn_indicator_history(' + str(start_time) + ',' +
                                   str(end_time) + ',\'' + indicator + '\',\'' + id + '\') AS (value DECIMAL, hour INTEGER)')
            # 将list转换为字典
            for i in range(len(data_list)):
                data_dic.update({data_list[i][1]: data_list[i][0]})

        for j in range(days * 24):
            y = data_dic.get(j)
            if y is None:
                y = 'NA'

            x1 = time.localtime(start_time + j * 3600)
            x2 = time.localtime(start_time + (j + 1) * 3600)
            time_x1 = time.strftime('%Y-%m-%d %H:%M', x1)
            time_x2 = time.strftime('%Y-%m-%d %H:%M', x2)

            if indicator == 'battery':
                value_arr.append({'time': time_x1 + '~' + time_x2, 'value': round(float(100 - 0.2 * j), 2)})
            else:
                value_arr.append({'time': time_x1 + '~' + time_x2, 'value': str(y)})
    except Exception, e:
        log.error(e.message)
    if indicator == 'battery':
        return JsonResponse({'battery': value_arr}, safe=True, status=status.HTTP_200_OK)
    else:
        return JsonResponse({indicator: value_arr}, safe=True, status=status.HTTP_200_OK)


# 租赁平台调用历史曲线
@api_view(['GET'])
def rent_container_history(request):
    deviceid = request.GET.get('deviceid')
    indicator = request.GET.get('indicator')
    day = request.GET.get('day')

    end_time = int(time.mktime(time.strptime(day, '%Y-%m-%d'))) + 3600 * 24
    start_time = end_time - 3600 * 24

    data_list = query_list('SELECT * FROM iot.fn_indicator_history(' + str(start_time) + ',' +
                           str(end_time) + ',\'' + indicator + '\',\'' + deviceid + '\') AS (value DECIMAL, hour INTEGER)')

    data_dic = {}
    value_arr = []
    for i in range(len(data_list)):
        data_dic.update({data_list[i][1]: data_list[i][0]})

    for j in range(24):
        y = data_dic.get(j)
        if y is None:
            y = 0

        x1 = time.localtime(start_time + j * 3600)
        x2 = time.localtime(start_time + (j + 1) * 3600)
        time_x1 = time.strftime('%H:%M', x1)
        time_x2 = time.strftime('%H:%M', x2)
        value_arr.append({'time': time_x1 + '~' + time_x2, 'value': float(y)})
    return JsonResponse({'data': {indicator: value_arr}, 'code': '0000', 'msg': 'Succ'},
                        safe=True, status=status.HTTP_200_OK)


# 租赁平台查询实时报文
@api_view(['GET'])
def rent_real_time_msg(request):
    deviceid = request.GET.get('deviceid')
    data = SensorData.objects.filter(deviceid=deviceid).order_by('-timestamp')
    if len(data) > 0:
        last_data = data[0]
        temperature = last_data.temperature
        humidity = last_data.humidity
        latitude = cal_position(last_data.latitude)
        longitude = cal_position(last_data.longitude)
        position_name = gps_info_trans(str(cal_position(last_data.latitude)) + ',' +
                                       str(cal_position(last_data.longitude)))
    else:
        temperature = 0
        humidity = 0
        position_name = ''
        latitude = 0
        longitude = 0
    return JsonResponse({'data': {'temperature': temperature,
                                  'humidity': humidity,
                                  'position_name': position_name,
                                  'latitude': latitude,
                                  'longitude': longitude},
                         'code': '0000', 'msg': 'Succ'},
                        safe=True, status=status.HTTP_200_OK)


@api_view(['POST'])
# @authentication_classes((SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication))
# @permission_classes((IsAuthenticated,))
def analysis_result(request):
    # if request.user.has_perm('view_containerrentinfo'):
    #     return JsonResponse({}, safe=True, status=status.HTTP_403_FORBIDDEN)
    # else:
    response = get_analysis_report()
    return JsonResponse(response, safe=True, status=status.HTTP_200_OK)


@api_view(['GET'])
def operation_overview(request):
    sql_1 = 'select count(1) from iot.monservice_boxinfo'
    sql_2 = 'select count(1) from iot.monservice_siteinfo'
    sql_3 = 'select sum(volume) from iot.monservice_siteinfo'

    container_num = query_list(sql_1)
    site_num = query_list(sql_2)
    volume = query_list(sql_3)
    box_distribution = Province.objects.raw('select count(1) as cnt,monservice_province.province_id,province_name '
                                           'from iot.monservice_boxinfo monservice_boxinfo '
                                           'left join iot.monservice_siteinfo monservice_siteinfo '
                                           'on monservice_boxinfo.siteinfo_id = monservice_siteinfo.id '
                                           'left join iot.monservice_province monservice_province '
                                           'on monservice_siteinfo.province_id = monservice_province.province_id '
                                           'group by monservice_province.province_id,province_name')
    distribution_dict = {}
    for item in list(box_distribution):
        cnt = item.cnt
        province_name = item.province_name
        if province_name is None:
            province_name = '运输中'
        distribution_dict[province_name] = cnt

    return JsonResponse({'container_num': container_num[0][0],
                         'site_num': site_num[0][0],
                         'volume': (volume[0][0], 0)[volume[0][0] is None],
                         'container_location': distribution_dict}, safe=True, status=status.HTTP_200_OK)


# 云箱安全参数
@api_view(['GET'])
def get_security_config(request):
    return_data = []
    data = query_list('select id, box_type_name,box_type_detail,interval_time,'
                      'temperature_threshold_min,temperature_threshold_max,'
                      'humidity_threshold_min,humidity_threshold_max,'
                      'collision_threshold_min,collision_threshold_max,'
                      'battery_threshold_min,battery_threshold_max,'
                      'operation_threshold_max,operation_threshold_min '
                      'from iot.box_type_info')
    for i in range(len(data)):
        return_data.append({'id': data[i][0],
                            'box_type_name': data[i][1],
                            'box_type_detail': data[i][2],
                            'interval_time': data[i][3],
                            'temperature_threshold_min': data[i][4],
                            'temperature_threshold_max': data[i][5],
                            'humidity_threshold_min': data[i][6],
                            'humidity_threshold_max': data[i][7],
                            'collision_threshold_min': data[i][8],
                            'collision_threshold_max': data[i][9],
                            'battery_threshold_min': data[i][10],
                            'battery_threshold_max': data[i][11],
                            'operation_threshold_max': data[i][12],
                            'operation_threshold_min': data[i][13]})

    return JsonResponse(return_data, safe=True, status=status.HTTP_200_OK)


# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


def strip_tuple(todo_list):
    strip_list = []
    if isinstance(todo_list, type([])):
        for query_item in todo_list:
            strip_list.append({'id': query_item[0], 'value': query_item[1]})
    return strip_list


# 判断当前位置与目的位置是否相同
def is_same_position(cur_longitude, cur_latitude, dst_longitude, dst_latitude):
    threshold = 0.01

    if abs(float(cur_longitude) - float(dst_longitude)) < threshold and abs(float(cur_latitude) - float(dst_latitude)) < threshold:
        return True
    else:
        return True


def get_utc(str_to_trans):
    if str_to_trans == 'NaN':
        str_current_utc = str(int(time.mktime(datetime.datetime.now().timetuple())))
        log.info("NaN mapping to: %s" % to_str(str_current_utc))
        return to_str(str_current_utc)
    else:
        return str_to_trans


# 判断指定的云箱id是否已经存在
def container_exists(container_id):
    sql = 'select count(1) as cnt from iot.box_info where deviceid = \'' + container_id + '\''
    result = query_list(sql)

    if result[0][0] > 0:
        return True
    else:
        return False


# 判断字符串是否是字典中的key
def key_exists(key, dictionary):
    if isinstance(dictionary, type({})):
        if key in dictionary.keys():
            return True
        else:
            return False
    else:
        return False


#geocode
def gps_info_trans(gpsinfo):
    '''
    :param gpsinfo: lat,lng for exmaple 39.92,116.46
    :return str:
    '''

    if gpsinfo == '0,0' or gpsinfo == '0.0,0.0':
        return ''

    ret_str = ''
    values = {}
    values['latlng'] = gpsinfo
    values['key'] = "AIzaSyA1Sr0UDr75ZZsymS4P12tBEzAt7zSl35o"
    data = urllib.urlencode(values)
    url = "https://ditu.google.cn/maps/api/geocode/json"
    geturl = url + "?" + data
    conn = redis.Redis(host="127.0.0.1", port=6379, db=0)
    if conn.hexists(REDIS_MAP_KEY, gpsinfo):
        ret_str = conn.hget(REDIS_MAP_KEY, gpsinfo)
    else:
        try:
            request = urllib2.Request(geturl)
            response = urllib2.urlopen(request)
            ret_dic = json.loads(response.read())
            log.info("req response: %s" % ret_dic)
            log.info("req url: %s" % geturl)
            if ret_dic['status'] == 'OK':
                ret_str = ret_dic['results'][0]['formatted_address']
                conn.hset(REDIS_MAP_KEY, gpsinfo, ret_str)
            else:
                log.info("req response: %s" % ret_dic)
                return ''
        except Exception, e:
            log.error(repr(traceback.print_exc()))
            log.error("geturl is %s" % geturl)
    return ret_str


def get_current_gpsinfo(container_id):
    ret = {}
    result = query_list("select latitude,longitude from iot.sensor_data where deviceid='%s' order by id desc limit 1" % container_id)
    if result is None or len(result) == 0:
        ret['lng'] = 0
        ret['lat'] = 0
    else:
        ret['lng'] = float(cal_position(result[0][1]))
        ret['lat'] = float(cal_position(result[0][0]))
    return ret


def get_analysis_report():
    final_response = {}
    final_response['carrier_sales_revenue'] = 86230000
    final_response['profit_margin'] = 0.68
    final_response['carrier_orders'] = 3402000
    final_response['use_of_containers'] = 5927000
    ret1, ret2, ret3, ret4 = gen_random_param_list()
    final_response['transportation_category'] = {"airline": ret1, "highway": ret2, "ocean": ret3, "other": ret4}
    ret1, ret2, ret3, ret4 = gen_random_param_list()
    final_response['goods_category'] = {"fish": ret1, "beaf": ret2, "chip": ret3, "gold": ret4}
    x_axis_time_list = gen_x_axis_time_list()
    foo = random.SystemRandom()
    final_response['history_revenue'] = [{"time": x_axis_time_list[0], "value": foo.randint(1000, 2000)},
                                         {"time": x_axis_time_list[1], "value": foo.randint(2000, 3000)},
                                         {"time": x_axis_time_list[2], "value": foo.randint(3000, 4000)},
                                         {"time": x_axis_time_list[3], "value": foo.randint(4000, 5000)},
                                         {"time": x_axis_time_list[4], "value": foo.randint(5000, 6000)},
                                         {"time": x_axis_time_list[5], "value": foo.randint(7000, 8000)},
                                         {"time": x_axis_time_list[6], "value": foo.randint(8000, 9000)},
                                         {"time": x_axis_time_list[7], "value": foo.randint(9000, 10000)},
                                         {"time": x_axis_time_list[8], "value": foo.randint(10000, 11000)},
                                         {"time": x_axis_time_list[9], "value": foo.randint(12000, 13000)},
                                         {"time": x_axis_time_list[10], "value": foo.randint(13000, 14000)},
                                         {"time": x_axis_time_list[11], "value": foo.randint(15000, 16000)}
                                         ]
    final_response['history_profit_margin'] = [{"time": x_axis_time_list[0], "value": foo.uniform(0.1, 0.3)},
                                               {"time": x_axis_time_list[1], "value": foo.uniform(0.2, 0.3)},
                                               {"time": x_axis_time_list[2], "value": foo.uniform(0.3, 0.3)},
                                               {"time": x_axis_time_list[3], "value": foo.uniform(0.3, 0.3)},
                                               {"time": x_axis_time_list[4], "value": foo.uniform(0.4, 0.6)},
                                               {"time": x_axis_time_list[5], "value": foo.uniform(0.5, 0.6)},
                                               {"time": x_axis_time_list[6], "value": foo.uniform(0.5, 0.6)},
                                               {"time": x_axis_time_list[7], "value": foo.uniform(0.6, 0.6)},
                                               {"time": x_axis_time_list[8], "value": foo.uniform(0.7, 0.9)},
                                               {"time": x_axis_time_list[9], "value": foo.uniform(0.7, 0.9)},
                                               {"time": x_axis_time_list[10], "value": foo.uniform(0.8, 0.9)},
                                               {"time": x_axis_time_list[11], "value": foo.uniform(0.8, 0.9)}
                                              ]
    final_response['history_orders'] = [{"time": x_axis_time_list[0], "value": foo.randint(1000, 2000)},
                                         {"time": x_axis_time_list[1], "value": foo.randint(2000, 3000)},
                                         {"time": x_axis_time_list[2], "value": foo.randint(3000, 4000)},
                                         {"time": x_axis_time_list[3], "value": foo.randint(4000, 5000)},
                                         {"time": x_axis_time_list[4], "value": foo.randint(5000, 6000)},
                                         {"time": x_axis_time_list[5], "value": foo.randint(7000, 8000)},
                                         {"time": x_axis_time_list[6], "value": foo.randint(8000, 9000)},
                                         {"time": x_axis_time_list[7], "value": foo.randint(9000, 10000)},
                                         {"time": x_axis_time_list[8], "value": foo.randint(10000, 11000)},
                                         {"time": x_axis_time_list[9], "value": foo.randint(12000, 13000)},
                                         {"time": x_axis_time_list[10], "value": foo.randint(13000, 14000)},
                                         {"time": x_axis_time_list[11], "value": foo.randint(15000, 16000)}
                                        ]
    final_response['history_use_of_containers'] = [{"time": x_axis_time_list[0], "value": foo.randint(1000, 2000)},
                                                   {"time": x_axis_time_list[1], "value": foo.randint(2000, 3000)},
                                                   {"time": x_axis_time_list[2], "value": foo.randint(3000, 4000)},
                                                   {"time": x_axis_time_list[3], "value": foo.randint(4000, 5000)},
                                                   {"time": x_axis_time_list[4], "value": foo.randint(5000, 6000)},
                                                   {"time": x_axis_time_list[5], "value": foo.randint(7000, 8000)},
                                                   {"time": x_axis_time_list[6], "value": foo.randint(8000, 9000)},
                                                   {"time": x_axis_time_list[7], "value": foo.randint(9000, 10000)},
                                                   {"time": x_axis_time_list[8], "value": foo.randint(10000, 11000)},
                                                   {"time": x_axis_time_list[9], "value": foo.randint(12000, 13000)},
                                                   {"time": x_axis_time_list[10], "value": foo.randint(13000, 14000)},
                                                   {"time": x_axis_time_list[11], "value": foo.randint(15000, 16000)}
                                                   ]
    return final_response


def gen_random_param_list():
    foo = random.SystemRandom()
    param1 = foo.uniform(0.1, 0.3)
    param2 = foo.uniform(0.1, 0.3)
    param3 = foo.uniform(0.1, 0.3)
    param4 = 1 - param1 - param2 - param3
    return param1, param2, param3, param4


#以月为单位，返回前1年的时间轴
def gen_x_axis_time_list():
    ret_time_list=[]
    cur_month = datetime.date.today().month
    cur_year = datetime.date.today().year
    print cur_month
    print cur_year
    if cur_month != 1:
        for num_last in range(cur_month, 13):
            ret_time_list.append("%s/%s" % (cur_year - 1, num_last))
        for num in range(1, cur_month):
            ret_time_list.append("%s/%s" % (cur_year, num))
    else:
        for num in range(1, 13):
            ret_time_list.append("%s/%s" % (cur_year - 1, num))
    return ret_time_list


#
# def get_operation_overview():
#     final_response = {}
#     foo = random.SystemRandom()
#     final_response['container_location'] = {"China": foo.randint(2000, 4000),
#                                             "USA": foo.randint(2000, 4000),
#                                             "Europe": foo.randint(1500, 3000),
#                                             "India": foo.randint(1500, 3000),
#                                             "Japan": foo.randint(1000, 2000),
#                                             "Canada": foo.randint(500, 1000),
#                                             "other": foo.randint(500, 1000)
#                                             }
#     container_num_int = 0
#     for item in final_response['container_location'].values():
#         container_num_int = container_num_int + item
#     final_response['container_num'] = container_num_int
#     final_response['container_on_lease'] = foo.randint(1000, container_num_int)
#     final_response['container_on_transportation'] = container_num_int - final_response['container_on_lease']
#     x_axis_time_list = gen_x_axis_time_list()
#     final_response['container_on_lease_history'] = [{"time": x_axis_time_list[0], "value": foo.randint(1000, 2000)},
#                                          {"time": x_axis_time_list[1], "value": foo.randint(2000, 3000)},
#                                          {"time": x_axis_time_list[2], "value": foo.randint(3000, 4000)},
#                                          {"time": x_axis_time_list[3], "value": foo.randint(4000, 5000)},
#                                          {"time": x_axis_time_list[4], "value": foo.randint(5000, 6000)},
#                                          {"time": x_axis_time_list[5], "value": foo.randint(7000, 8000)},
#                                          {"time": x_axis_time_list[6], "value": foo.randint(8000, 9000)},
#                                          {"time": x_axis_time_list[7], "value": foo.randint(9000, 10000)},
#                                          {"time": x_axis_time_list[8], "value": foo.randint(10000, 11000)},
#                                          {"time": x_axis_time_list[9], "value": foo.randint(12000, 13000)},
#                                          {"time": x_axis_time_list[10], "value": foo.randint(13000, 14000)},
#                                          {"time": x_axis_time_list[11], "value": foo.randint(15000, 16000)}
#                                          ]
#     final_response['container_on_transportation_history'] = [{"time": x_axis_time_list[0], "value": foo.randint(1000, 2000)},
#                                          {"time": x_axis_time_list[1], "value": foo.randint(2000, 3000)},
#                                          {"time": x_axis_time_list[2], "value": foo.randint(3000, 4000)},
#                                          {"time": x_axis_time_list[3], "value": foo.randint(4000, 5000)},
#                                          {"time": x_axis_time_list[4], "value": foo.randint(5000, 6000)},
#                                          {"time": x_axis_time_list[5], "value": foo.randint(7000, 8000)},
#                                          {"time": x_axis_time_list[6], "value": foo.randint(8000, 9000)},
#                                          {"time": x_axis_time_list[7], "value": foo.randint(9000, 10000)},
#                                          {"time": x_axis_time_list[8], "value": foo.randint(10000, 11000)},
#                                          {"time": x_axis_time_list[9], "value": foo.randint(12000, 13000)},
#                                          {"time": x_axis_time_list[10], "value": foo.randint(13000, 14000)},
#                                          {"time": x_axis_time_list[11], "value": foo.randint(15000, 16000)}
#                                         ]
#     return final_response


# 获取国家列表
@csrf_exempt
@api_view(['GET'])
def get_nation_list(request):
    ret_list = []
    nation_list = Nation.objects.filter(nation_name='中国').order_by('sorted_key')
    for item in nation_list:
        ret_list.append({'nation_id': item.nation_id, 'nation_name': item.nation_name})

    return JsonResponse({'data': ret_list}, safe=True, status=status.HTTP_200_OK)


# 根据国家获取省列表
@csrf_exempt
@api_view(['GET'])
def get_province_list(request, nation_id):
    ret_list = []
    province_list = Province.objects.filter(nation_id=nation_id).order_by('zip_code')
    for item in province_list:
        ret_list.append({'province_id': item.province_id, 'province_name': item.province_name})

    return JsonResponse({'data': ret_list}, safe=True, status=status.HTTP_200_OK)


# 根据省获取城市列表
@csrf_exempt
@api_view(['GET'])
def get_city_list(request, province_id):
    ret_list = []
    city_list = City.objects.filter(province_id=province_id).order_by('sorted_key')
    for item in city_list:
        ret_list.append({'city_id': item.id, 'city_name': item.city_name,
                         'longitude': item.longitude, 'latitude': item.latitude})
    return JsonResponse({'data': ret_list}, safe=True, status=status.HTTP_200_OK)


# 根据地点名称获取经纬度
@csrf_exempt
@api_view(['POST'])
def get_lnglat(request):
    position_name = json.loads(request.body)['position_name']
    data = get_lng_lat(to_str(position_name))
    return JsonResponse({'position_name': position_name,
                         'longitude': data['longitude'], 'latitude': data['latitude']},
                        safe=True, status=status.HTTP_200_OK)


# 根据经纬度查询地名
@csrf_exempt
@api_view(['POST'])
def get_position(request):
    longitude = json.loads(request.body)['longitude']
    latitude = json.loads(request.body)['latitude']
    position_name = get_position_name(longitude, latitude)
    if position_name <> 'OVER_QUERY_LIMIT' and position_name <> '':
        city_data = City.objects.extra(select=None,
                                       where=['POSITION(city_name IN %s) > 0',
                                              'POSITION(nation_name IN %s) > 0',
                                              'POSITION(state_name IN %s) > 0',
                                              ], params=[position_name, position_name, position_name])
        if len(city_data) > 0:
            nation_id = city_data[0].nation_id
            province_id = city_data[0].province_id
            city_id = city_data[0].id
            nation_name = city_data[0].nation_name
            province_name = city_data[0].state_name
            city_name = city_data[0].city_name

        else:
            nation_id = 0
            province_id = 0
            city_id = 0
            nation_name = ''
            province_name = ''
            city_name = ''

        return JsonResponse({'position_name': position_name, 'nation_id': nation_id,
                             'province_id': province_id, 'city_id': city_id,
                             'nation_name': nation_name, 'province_name': province_name,
                             'city_name': city_name}, safe=True, status=status.HTTP_200_OK)
    else:
        if position_name == 'OVER_QUERY_LIMIT':
            return JsonResponse({'msg': 'OVER_QUERY_LIMIT'}, safe=True, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'msg': 'location name not found'}, safe=True, status=status.HTTP_200_OK)


# 查询所有类型箱子安全参数
@csrf_exempt
@api_view(['GET'])
def get_all_safe_settings(request):
    try:
        box_types = BoxTypeInfo.objects.all().order_by('id')
        types_ser = BoxTypeInfoSerializer(box_types, many=True)
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get all box safe settings success',
                        'box_types': types_ser.data}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 根据箱子类型ID查询安全参数
@csrf_exempt
@api_view(['GET'])
def get_safe_settings(request, type_id):
    try:
        box_type = BoxTypeInfo.objects.get(id=type_id)
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get box safe settings success', 'box_type': BoxTypeInfoSerializer(box_type).data}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 修改箱子安全参数
@csrf_exempt
@api_view(['PUT'])
def save_safe_settings(request, type_id):
    try:
        data = json.loads(request.body)
        box_type = BoxTypeInfo.objects.get(id=type_id)
        box_type.interval_time = data['interval_time']
        box_type.temperature_threshold_min = data['temperature_threshold_min']
        box_type.temperature_threshold_max = data['temperature_threshold_max']
        box_type.humidity_threshold_min = data['humidity_threshold_min']
        box_type.humidity_threshold_max = data['humidity_threshold_max']
        box_type.battery_threshold_min = data['battery_threshold_min']
        box_type.battery_threshold_max = data['battery_threshold_max']
        box_type.operation_threshold_min = data['operation_threshold_min']
        box_type.operation_threshold_max = data['operation_threshold_max']
        box_type.collision_threshold_min = data['collision_threshold_min']
        box_type.collision_threshold_max = data['collision_threshold_max']
        box_type.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'安全参数设置成功.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_message(request):
    alarm_count = AlarmInfo.objects.filter(alarm_status=1).count()
    dispatches = SiteDispatch.objects.filter(create_date__gte=datetime.date.today()).order_by('did')
    undispach_count = len(dispatches)
    message_count = alarm_count + undispach_count
    return JsonResponse({'alarm_count': alarm_count, 'undispach_count': undispach_count, 'message_count': message_count},
                        safe=True, status=status.HTTP_200_OK)




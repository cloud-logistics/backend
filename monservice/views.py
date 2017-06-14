#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
import datetime
import base64
import traceback
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from util.db import query_list, save_to_db
from util import logger
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from models import ContainerRentInfo
from serializers import ContainerRentInfoSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_jwt.settings import api_settings
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import urllib
import urllib2
import json


log = logger.get_logger('monservice.view.py')
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'mock_data.json'
NOT_APPLICABLE = 'NA'
ZERO = 0
STATUS_NORMAL = '正常'
STATUS_ABNORMAL = '异常'
IN_TRANSPORT = '在运'
ANCHORED = '停靠'


@csrf_exempt
def containers_overview(request):
    try:
        with open(str(file_path)) as f:
            load_dict = json.load(f)
        return JsonResponse(load_dict, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('containers_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False ,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def satellites_overview(request):
    try:
        with open(str(file_path)) as f:
            load_dict = json.load(f)
        return JsonResponse(load_dict, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('satellites_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 实时报文
@csrf_exempt
def realtime_message(request):
    try:
        id = json.loads(request.body)['containerId']
    except Exception, e:
        id = NOT_APPLICABLE
        log.error(e.message)

    if id == '':
        mock_json = '{"boxStatus": {"num_of_collide": {"status": "正常", "value": 32}, ' \
                    '"num_of_door_open": {"status": "正常", "value": 47}}, ' \
                    '"currentStatus": "在运", "carrier": "中集智能", "containerId": "TEST", ' \
                    '"containerType": "标准箱", "position": {"lat": 36.07, "lng": 120.33}, ' \
                    '"humidity": {"status": "正常", "value": 81.3}, "speed": 80.45, ' \
                    '"battery": {"status": "正常", "value": 0.8}, ' \
                    '"temperature": {"status": "正常", "value": 2.3}}' \
                    '"locationName":%s' % gps_info_trans("36.07,120.33")
        return JsonResponse(json.loads(mock_json), safe=False, status=status.HTTP_200_OK)

    # 获取承运方
    carrier_data = query_list('select carrier_info.carrier_name,order_info.srcid,order_info.dstid '
                              'from iot.order_info order_info '
                              'left join iot.box_order_relation box_order_relation on order_info.trackid = box_order_relation.trackid '
                              'left join iot.carrier_info carrier_info on order_info.carrierid = carrier_info.id '
                              'where box_order_relation.deviceid =  \'' + id + '\' '
                              'group by carrier_info.carrier_name,order_info.srcid,order_info.dstid')
    if len(carrier_data) > 0:
        carrier_name = carrier_data[0][0]
        srcid = carrier_data[0][1]
        dstid = carrier_data[0][2]
    else:
        carrier_name = NOT_APPLICABLE
        srcid = ZERO
        dstid = ZERO

    # 获取起始点经纬度
    src_site_data = query_list('select latitude,longitude from iot.site_info where id = ' + str(srcid) + '')
    if len(src_site_data) > 0:
        src_latitude = src_site_data[0][0]
        src_longitude = src_site_data[0][1]
    else:
        src_latitude = ZERO
        src_longitude = ZERO

    # 获取结束点经纬度
    dst_site_data = query_list('select latitude,longitude from iot.site_info where id = ' + str(dstid) + '')
    if len(dst_site_data) > 0:
        dst_latitude = dst_site_data[0][0]
        dst_longitude = dst_site_data[0][1]
    else:
        dst_latitude = ZERO
        dst_longitude = ZERO

    # 获取云箱型号
    box_type_data = query_list('select box_type_info.box_type_name from iot.box_info box_info '
                               'left join iot.box_type_info box_type_info on box_info.type = box_type_info.id '
                               'where box_info.deviceid = \'' + id + '\' group by box_type_info.box_type_name')

    if len(box_type_data) > 0:
        box_type = box_type_data[0][0]
    else:
        box_type = NOT_APPLICABLE

    # 获取传感器数据
    sensor_data = query_list('select temperature,humidity,longitude,latitude,speed,collide '
                             'from iot.sensor_data where deviceid = \'' + id + '\' order by timestamp desc limit 1')
    if len(sensor_data) > 0:
        temperature = sensor_data[0][0]
        humidity = sensor_data[0][1]
        longitude = cal_position(sensor_data[0][2])
        latitude = cal_position(sensor_data[0][3])
        speed = sensor_data[0][4]
        collide = sensor_data[0][5]
    else:
        temperature = ZERO
        humidity = ZERO
        longitude = ZERO
        latitude = ZERO
        speed = ZERO
        collide = ZERO

    # 获取箱子阈值
    threshold_data = query_list('select temperature_threshold_max,temperature_threshold_min,'
                                'humidity_threshold_max,humidity_threshold_min,'
                                'collision_threshold_max,collision_threshold_min,'
                                'battery_threshold_max,battery_threshold_min,'
                                'operation_threshold_max,operation_threshold_min ' \
                                'from iot.box_info box_info ' \
                                'INNER join iot.box_type_info box_type_info on box_info.type = box_type_info.id '
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
        operation_threshold_min =  threshold_data[0][9]

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
    if not is_same_position(longitude, latitude, src_longitude, src_latitude) and \
            not is_same_position(longitude, latitude, dst_longitude, dst_latitude):
        shipping_status = IN_TRANSPORT
    else:
        shipping_status = ANCHORED

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
    battery = 0.6           # 后续需要修改为真实值
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
    num_of_door_open = 54   # 后续需要修改为真实值
    if operation_threshold_min <= int(num_of_door_open) <= operation_threshold_max:
        door_open_status = STATUS_NORMAL
    else:
        door_open_status = STATUS_ABNORMAL

    ret_data = {'containerId': id,
                'containerType': box_type,
                'currentStatus': shipping_status,
                'carrier': carrier_name, 'position': {'lng': longitude, 'lat': latitude},
                'speed': float(speed),
                'temperature': {'value': float(temperature), 'status': temperature_status},
                'humidity': {'value': float(humidity), 'status': humidity_status},
                'battery': {'value': float(battery), 'status': battery_status},
                'boxStatus': {'num_of_collide': {'value': int(collide), 'status': collide_status},
                              'num_of_door_open': {'value': int(num_of_door_open), 'status': door_open_status}}}
    return JsonResponse(ret_data, safe=False, status=status.HTTP_200_OK)


# 实时位置
@csrf_exempt
def realtime_position(request):
    try:
        id = json.loads(request.body)['containerId']
    except Exception, e:
        id = NOT_APPLICABLE
        log.error(e.message)

    data = query_list(
        'select box_info.deviceid, carrier_info.carrier_name, site_info_src.location, site_info_dst.location '
        'from iot.box_info box_info '
        'left join iot.box_order_relation relation on box_info.deviceid = relation.deviceid '
        'left join iot.order_info order_info on order_info.trackid = relation.trackid '
        'left join iot.carrier_info carrier_info on carrier_info.id = order_info.carrierid '
        'left join iot.site_info site_info_src on site_info_src.id = order_info.srcid '
        'left join iot.site_info site_info_dst on site_info_dst.id = order_info.dstid '
        'where box_info.deviceid = \'' + id + '\' '
        'group by box_info.deviceid,carrier_info.carrier_name, site_info_src.location, site_info_dst.location')

    if len(data) > 0:
        clientid = to_str(data[0][0])
        carrier = to_str(data[0][1])
        origination = to_str(data[0][2])
        destination = to_str(data[0][3])
    else:
        clientid = NOT_APPLICABLE
        carrier = NOT_APPLICABLE
        origination = NOT_APPLICABLE
        destination = NOT_APPLICABLE

    ori_data = query_list('select latitude, longitude from iot.site_info where location = \'' + origination + '\'')
    dst_data = query_list('select latitude, longitude from iot.site_info where location = \'' + destination + '\'')
    if len(ori_data) > 0:
        ori_latitude = float(to_str(ori_data[0][0]))
        ori_longitude = float(to_str(ori_data[0][1]))
    else:
        ori_latitude = ZERO
        ori_longitude = ZERO

    if len(dst_data) > 0:
        dst_latitude = float(to_str(dst_data[0][0]))
        dst_longitude = float(to_str(dst_data[0][1]))
    else:
        dst_latitude = ZERO
        dst_longitude = ZERO

    cur_data = query_list('select latitude,longitude from iot.sensor_data '
                          'where deviceid = \'' + clientid + '\' order by timestamp desc limit 1')
    if len(cur_data) > 0:
        cur_latitude = cal_position(cur_data[0][0])
        cur_longitude = cal_position(cur_data[0][1])
    else:
        cur_latitude = ZERO
        cur_longitude = ZERO
    start_location_name = gps_info_trans("%s,%s" % (ori_latitude, ori_longitude))
    end_location_name = gps_info_trans("%s,%s" % (dst_latitude, dst_longitude))
    cur_location_name = gps_info_trans("%s,%s" % (cur_latitude, cur_longitude))
    ret_data = {'containerInfo': {'containerId': clientid, 'carrier': carrier},
                'startPosition': {'lng': ori_longitude, 'lat': ori_latitude},
                'startLocationName': start_location_name,
                'currentPosition': {'lng': cur_longitude, 'lat': cur_latitude},
                'currentLocationName': cur_location_name,
                'endPosition': {'lng': dst_longitude, 'lat': dst_latitude},
                'endLocationName': end_location_name
                }

    return JsonResponse(ret_data, safe=False, status=status.HTTP_200_OK)


# 报警监控
@csrf_exempt
def alarm_monitor(request):
    data = query_list('select alarm_info.deviceid,alert_level_info.level,alarm_info.timestamp,'
                      'alert_code_info.description,alarm_info.code,alarm_info.status,'
                      'carrier_info.carrier_name,alarm_info.longitude,alarm_info.latitude,'
                      'alarm_info.speed,alarm_info.temperature,alarm_info.humidity,'
                      'alarm_info.num_of_collide,alarm_info.num_of_door_open,'
                      'alarm_info.battery,alarm_info.robert_operation_status '
                      'from iot.alarm_info alarm_info '
                      'left join iot.alert_level_info alert_level_info on alarm_info.level = alert_level_info.id '
                      'left join iot.alert_code_info alert_code_info on alarm_info.code = alert_code_info.errcode '
                      'left join iot.carrier_info carrier_info on carrier_info.id = carrier order by timestamp desc')
    ret_data = []

    for record in data:
        deviceid = record[0]
        level = record[1]
        timestamp = record[2] * 1000        # 前端显示需要精确到毫秒
        error_description = record[3]
        error_code = record[4]
        ship_status = record[5]
        carrier_name = record[6]
        longitude = cal_position(record[7])
        latitude = cal_position(record[8])
        speed = record[9]
        temperature = record[10]
        humidity = record[11]
        num_of_collide = record[12]
        num_of_door_open = record[13]
        battery = record[14]
        robert_operation_status = record[15]
        location_name = gps_info_trans("%s,%s" % (latitude, longitude))
        ret_data.append({'containerId': deviceid, 'alertTime': timestamp, 'alertLevel': level,
                         'alertType': error_description, 'alertCode': str(error_code), 'status': ship_status,
                         'carrier': carrier_name, 'position': {'lng': float(longitude), 'lat': float(latitude)},
                         'speed': float(speed), 'temperature': float(temperature), 'humidity': float(humidity),
                         'num_of_collide': float(num_of_collide), 'num_of_door_open': float(num_of_door_open),
                         'battery': float(battery), 'robertOperationStatus': robert_operation_status,
                         'locationName': location_name})
    return JsonResponse({'alerts': ret_data}, safe=False, status=status.HTTP_200_OK)


# 基础信息查询
@csrf_exempt
def basic_info(request):
    data = query_list('select box_info.deviceid, box_type_info.box_type_name, produce_area_info.address, '
                      'manufacturer_info.name, carrier_info.carrier_name, date_of_production '
                      'from iot.box_info box_info '
                      'left join iot.box_type_info on box_info.type = box_type_info.id '
                      'left join iot.box_order_relation box_order_relation on box_order_relation.deviceid = box_info.deviceid '
                      'left join iot.order_info order_info on order_info.trackid = box_order_relation.trackid '
                      'left join iot.carrier_info on order_info.carrierid = carrier_info.id '
                      'left join iot.produce_area_info produce_area_info on box_info.produce_area = produce_area_info.id '
                      'left join iot.manufacturer_info manufacturer_info on box_info.manufacturer = manufacturer_info.id '
                      'group by box_info.deviceid, box_type_name, produce_area_info.address, manufacturer_info.name, '
                      'carrier_name, date_of_production')
    ret_list = []
    for item in data:
        dicitem = {}
        dicitem['containerId'] = to_str(item[0])
        dicitem['containerType'] = to_str(item[1])
        dicitem['factoryLocation'] = to_str(item[2])
        dicitem['factory'] = to_str(item[3])
        dicitem['carrier'] = to_str(item[4])
        dicitem['factoryDate'] = to_str(item[5])
        ret_list.append(dicitem)

    ret_dic = {'basicInfo': ret_list}

    return JsonResponse(ret_dic, safe=False, status=status.HTTP_200_OK)


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
                        from iot.order_info where iot.order_info.trackid
                        in (select trackid from iot.box_order_relation
                        where iot.box_order_relation.deviceid = '%s')''' % param_dic['containerId']
                order_info_query_list = query_list(query_template)
                site_info_query_list = query_list('select id, latitude, longitude from iot.site_info')
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
                            start_dic['localtionName'] = gps_info_trans(str(start_dic['position']['lat']) +
                                                                        ',' + str(start_dic['position']['lng']))
                        end_dic = {}
                        end_dic['time'] = item[3]
                        if item[1] in site_info_dic.keys():
                            end_dic['position'] = site_info_dic[item[1]]
                            end_dic['localtionName'] = gps_info_trans(str(end_dic['position']['lat']) +
                                                                        ',' + str(end_dic['position']['lng']))
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
            return JsonResponse(final_response, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse(final_response, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def history_message(request):
    param = to_str(request.body)
    param_dic = {}
    final_response = {}
    json_record_list = []
    container_id_final = ""
    container_type_final = ""
    query_start_time = 0
    query_end_time = 0
    if param:
        try:
            param_dic = json.loads(param)
            if key_exists('containerId', param_dic):
                container_id = param_dic['containerId']
                if key_exists('containerType', param_dic):
                    container_type = int(param_dic['containerType'])
                    sql = "select deviceid from iot.box_info where type = %s " % container_type
                    deviceid_tuple_list = query_list(sql)
                    deviceid_list = []
                    for item in deviceid_tuple_list:
                        if item[0]:
                            deviceid_list.append(item[0])
                    if container_id in deviceid_list:
                        container_id_final = container_id
                    #
                    sql_query_box_type_info = "select box_type_name from iot.box_type_info where id=%s " % container_type
                    box_type_name_tuple_list = query_list(sql_query_box_type_info)
                    for item in box_type_name_tuple_list:
                        if item[0]:
                            container_type_final = item[0]

                else:
                    container_id_final = container_id
            if key_exists('startTime', param_dic) and key_exists('endTime', param_dic):
                query_start_time_str = param_dic['startTime']
                query_end_time_str = param_dic['endTime']
                if len(query_start_time_str) > 10:
                    query_start_time = int(query_start_time_str) / 1000
                else:
                    query_start_time = int(query_start_time_str)
                if len(query_end_time_str) > 10:
                    query_end_time = int(query_end_time_str) / 1000
                else:
                    query_end_time = int(query_end_time_str)
            history_sql_template = "select deviceid, timestamp, temperature, humidity, longitude, latitude, speed, collide, light, legacy" \
                                   " from iot.sensor_data where deviceid = '%s' and timestamp >= %d and timestamp < %d limit 100"
            query_result_tuple_list = query_list(history_sql_template % (container_id_final, query_start_time, query_end_time))
            log.debug("query_result_tuple_list:%s" % query_result_tuple_list)
            for query_tuple in query_result_tuple_list:
                detail_message_dict = {}
                each_record_dicteach_record_dict = {}
                detail_message_dict['device_id'] = query_tuple[0]
                detail_message_dict['utc'] = query_tuple[1]
                detail_message_dict['temp'] = query_tuple[2]
                detail_message_dict['humi'] = query_tuple[3]
                detail_message_dict['longitude'] = query_tuple[4]
                detail_message_dict['latitude'] = query_tuple[5]
                detail_message_dict['speed'] = query_tuple[6]
                detail_message_dict['collide'] = query_tuple[7]
                detail_message_dict['light'] = query_tuple[8]
                detail_message_dict['legacy'] = query_tuple[9]
                detail_message_str = base64.b64encode(json.dumps(detail_message_dict))
                each_record_dicteach_record_dict['record'] = detail_message_str
                each_record_dicteach_record_dict['containerId'] = container_id_final
                each_record_dicteach_record_dict['containerType'] = container_type_final
                each_record_dicteach_record_dict['time'] = detail_message_dict['utc']
                each_record_dicteach_record_dict['messageType'] = to_str("标准报文")
                json_record_list.append(each_record_dicteach_record_dict)
            #final
            final_response['result'] = json_record_list
            log.debug(json.dumps(final_response))
            return JsonResponse(final_response, safe=False, status=status.HTTP_200_OK)
        except Exception, e:
            log.error(repr(traceback.print_exc()))
            return JsonResponse(final_response, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(final_response, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def status_summary(request):
    pass


# 基础信息管理
@csrf_exempt
def basic_info_manage(request):
    pass


# 云箱基础信息录入
@csrf_exempt
def basic_info_config(request):
    try:
        response_msg = 'internal error.'
        data = json.loads(request.body)
        container_id = to_str(data['containerId'])              # 云箱id
        date_of_production = to_str(data['manufactureTime'])    # 生产日期
        battery_info = to_str(data['batteryInfo'])              # 电源信息
        manufacturer = to_str(data['factory'])                  # 生产厂家
        produce_area = to_str(data['factoryLocation'])          # 生产地点
        hardware_info = to_str(data['hardwareInfo'])            # 智能硬件信息
        carrier = to_str(data['carrier'])                       # 承运人

        sql = 'insert into iot.box_info(deviceid, type, date_of_production, manufacturer, produce_area, ' \
              'hardware, battery, carrier) ' \
              'VALUES (\'' + container_id + '\', 1, \'' + date_of_production + '\',' + str(manufacturer) + ',' \
              + str(produce_area) + ',' + str(hardware_info) + ',' + str(battery_info) + ',' + str(carrier) + ')'

        flag = container_exists(container_id)
        if not flag:
            # 云箱id不存在就保存
            save_to_db(sql)
            response_msg = 'save successfully.'
        else:
            response_msg = 'save failed, container id already exists.'

    except Exception, e:
        log.error(e.message)
    finally:
        return JsonResponse(response_msg, safe=False, status=status.HTTP_200_OK)


@csrf_exempt
def options_to_show(request):
    final_response = {}
    req_param_str_utf8 = to_str(request.body)
    req_param = json.loads(req_param_str_utf8)
    if req_param:
        if req_param['requiredOptions']:
            for item in req_param['requiredOptions']:
                if item == 'alertLevel':
                    alert_level_list = query_list('select id,level from iot.alert_level_info')
                    final_response['alertLevel'] = strip_tuple(alert_level_list)
                if item == 'alertCode':
                    alert_code_list = query_list('select id,errcode from iot.alert_code_info')
                    final_response['alertCode'] = strip_tuple(alert_code_list)
                if item == 'alertType':
                    alert_type_list = query_list('select id,type from iot.alert_type_info')
                    final_response['alertType'] = strip_tuple(alert_type_list)
                if item == 'containerType':
                    container_type_list = query_list('select id,box_type_name from iot.box_type_info')
                    final_response['containerType'] = strip_tuple(container_type_list)
                if item == 'currentStatus':
                    status_list = []
                    status_list.append(to_str(IN_TRANSPORT))
                    status_list.append(to_str(ANCHORED))
                    final_response['currentStatus'] = status_list
                if item == 'location':
                    location_list = query_list('select id,location from iot.site_info')
                    final_response['location'] = strip_tuple(location_list)
                if item == 'carrier':
                    carrier_list = query_list('select id,carrier_name from iot.carrier_info')
                    final_response['carrier'] = strip_tuple(carrier_list)
                if item == 'factory':
                    factory_list = query_list('select id,name from iot.manufacturer_info')
                    final_response['factory'] = strip_tuple(factory_list)
                if item == 'factoryLocation':
                    location_list = query_list('select id,address from iot.produce_area_info')
                    final_response['factoryLocation'] = strip_tuple(location_list)
                if item == 'batteryInfo':
                    batteryinfo_list = query_list('select id,battery_detail from iot.battery_info')
                    final_response['batteryInfo'] = strip_tuple(batteryinfo_list)
                if item == 'maintenanceLocation':
                    location_list = query_list('select id,location from iot.maintenance_info')
                    final_response['maintenanceLocation'] = strip_tuple(location_list)
                if item == 'intervalTime':
                    interval_time_list = query_list('select id,interval_time_min from iot.interval_time_info')
                    # interval time type is integer
                    final_response['intervalTime'] = strip_tuple(interval_time_list)
                if item == 'hardwareInfo':
                    hardware_info_list = query_list('select id,hardware_detail from iot.hardware_info')
                    final_response['hardwareInfo'] = strip_tuple(hardware_info_list)
            log.debug(json.dumps(final_response))
            return JsonResponse(final_response, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse(req_param, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(req_param, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def security_config(request):
    final_response = {}
    req_param_str_utf8 = to_str(request.body)
    req_param = json.loads(req_param_str_utf8)
    append_sql = lambda x,y : x + y + ','
    final_append_sql = lambda x, y: x + y
    sql_template = '''update iot.box_type_info set %s'''
    column_string = ''
    if req_param:
        container_type_list = query_list('select id from iot.box_type_info')
        final_type_list = strip_tuple(container_type_list, 0)
        log.info("safe_param_to_set: final_type_list = %s" % final_type_list)
        log.info("safe_param_to_set: containerType = %s" % req_param['containerType'])
        if int(req_param['containerType']) in final_type_list:
            insert_key_list = req_param.keys()
            if 'intervalTime' in insert_key_list:
                # column_string = column_string + 'intervalTime' + ','
                interval_value_list = query_list("select interval_time_min from iot.interval_time_info where id = '%s'"
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
                return JsonResponse(final_response, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return JsonResponse(final_response, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse(req_param, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(req_param, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication))
@permission_classes((IsAuthenticated,))
def mycontainers(request):
    if request.user.has_perm('view_containerrentinfo'):
        ret_dict = {}
        ret = ContainerRentInfo.objects.all()
        serializer = ContainerRentInfoSerializer(ret, many=True)
        # print repr(serializer.data)
        ret_dict['results'] = serializer.data
        log.info(ret_dict)
        return JsonResponse(ret_dict, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({}, safe=False, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def containers_on_release(request):
    pass


@api_view(['GET'])
def containers_available(request):
    pass


@api_view(['POST'])
def verify_user(request):
    req_param_str_utf8 = to_str(request.body)
    req_param = json.loads(req_param_str_utf8)
    user = authenticate(username=req_param['username'], password=req_param['password'])
    ret_dict ={}
    if user is not None:
        u = User.objects.get(username=req_param['username'])
        if u.has_perm('monservice.view_containerrentinfo'):
            ret_dict['role'] = 'carrier'
        else:
            ret_dict['role'] = 'admin'
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(u)
        token = jwt_encode_handler(payload)
        ret_dict['token'] = token
        return JsonResponse(ret_dict, safe=False, status=status.HTTP_200_OK)


# 向终端发送command
@authentication_classes((SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication))
@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def send_command(request):
    action = json.loads(request.body)['action']
    id = json.loads(request.body)['containerId']
    id = "9ccb696844bdcb880efb7fc18c5361a6221de9ad"
    conn = redis.Redis(host="127.0.0.1", port=6379, db=0)
    conn.rpush('command_list',
               "{\"service\":\"command\",\"action\": \"" + action + "\",\"result\":\"123\",\"id\":\"" + id + "\"}")
    conn.save()
    return JsonResponse({"code": "200"}, safe=False, status=status.HTTP_200_OK)


# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


# 将传感器数据的经度或纬度转换为小数点形式，Longitude: 116296046, //dddmmmmmm   Latitude: 39583032,  //ddmmmmmm
def cal_position(value):
    hour = value[:-6]
    minute = value[len(hour):len(value)]

    return float(hour + '.' + minute)


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
        return False


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
    ret_str = ''
    values = {}
    values['latlng'] = gpsinfo
    values['key'] = "AIzaSyDD2vDhoHdl8eJAIyWPv0Jw7jeO6VtlRF8"
    data = urllib.urlencode(values)
    url = "https://ditu.google.cn/maps/api/geocode/json"
    geturl = url + "?" + data
    try:
        request = urllib2.Request(geturl)
        response = urllib2.urlopen(request)
        ret_dic = json.loads(response.read())
        if ret_dic['status'] == 'OK':
            ret_str = ret_dic['results'][0]['formatted_address']
    except Exception, e:
        log.error(repr(traceback.print_exc()))
        log.error("geturl is %s" % geturl)
    return ret_str

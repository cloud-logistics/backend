#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from util.db import save_to_db, query_list
from util.geo import cal_position
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
# Create your views here.
from rest_framework import status
from util import logger
from operator import itemgetter
from sensor.errcode import *
from util.geo import get_distance
from util.geo import cal_speed

from monservice.models import SensorData
import time
import zipfile
import os
from django.http import StreamingHttpResponse


# logging
log = logger.get_logger('view.py')
RESULT_200_OK = {'result': 'ok', 'code': '200'}
RESULT_400_BAD_REQUEST = {'result': 'bad request', 'code': '400'}


@csrf_exempt
def input_data(request):

    if request.method == 'POST' or request.method == 'PUT':
        try:
            log.debug('receive request body:' + request.body)
            data_list = parse(request.body)
            sql = build_sql(data_list)
            save_to_db(sql)
            log.info('insert data to database successfully')
            return JsonResponse(RESULT_200_OK, status=status.HTTP_200_OK, safe=True)
        except Exception, e:
            log.error('save to db error, msg: ' + e.__str__())
            return JsonResponse(RESULT_400_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST, safe=True)
    else:
        log.error('bad request method. please use POST/PUT.')
        return JsonResponse(RESULT_400_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST, safe=True)


# 解析数据
def parse(msg):
    body = json.loads(str(msg))
    s = body['data']
    meta = body['meta']
    deviceid = str(s['deviceid'])
    endpointid = str(meta['endpointId'])
    legacy = str(s['legacy'])
    data_list = []

    if '' == legacy:
        # legacy为空时时正常非断网续传情况
        timestamp = s['utc']
        temperature = s['temp']
        humidity = s['humi']
        longitude = s['longitude']
        latitude = s['latitude']
        speed = s['speed']
        collide = s['collide']
        light = s['light']

        data_list = data_list + [{'timestamp': timestamp, 'deviceid': deviceid,
                                  'temperature': temperature, 'humidity': humidity,
                                  'latitude': latitude, 'longitude': longitude,
                                  'speed': speed, 'collide': collide, 'light': light, 'endpointid': endpointid}]

    else:
        # legacy字段不为空时，数据格式以$开始，多个字段以#分割，例如：
        # $utc#temperature#humidity#longitude#latitude#speed#collidetimes#light
        # $1#24#26#0#0#0#0#0$1495515476#24#26#108501390#34127504#0#0#43
        data = legacy.split('$')
        size = data.__len__()

        for i in range(1, size):
            elements = data[i].split('#')
            if elements.__len__() >= 8:
                timestamp = elements[0]
                temperature = elements[1]
                humidity = elements[2]
                longitude = elements[3]
                latitude = elements[4]
                speed = elements[5]
                collide = elements[6]
                light = elements[7]
                data_list = data_list + \
                            [{'timestamp': timestamp, 'deviceid': deviceid,
                              'temperature': temperature, 'humidity': humidity,
                              'latitude': latitude, 'longitude': longitude,
                              'speed': speed, 'collide': collide, 'light': light, 'endpointid': endpointid}]

            else:
                log.error('legacy format error, legacy: ' + legacy)

    return data_list


def build_sql(data_list):
    sql = 'insert into iot.monservice_sensordata(timestamp, deviceid, temperature, humidity, latitude, longitude, ' \
          'speed, collide, light, endpointid) values '
    size = data_list.__len__()

    for i in range(size):
        data = data_list[i]
        sql = sql + '(' + str(data['timestamp']) + ',\'' + \
            str(data['deviceid']) + '\',\'' + \
            str(data['temperature']) + '\',\'' + \
            str(data['humidity']) + '\',\'' + \
            str(data['latitude']) + '\',\'' + \
            str(data['longitude']) + '\',\'' + \
            str(data['speed']) + '\',\'' + \
            str(data['collide']) + '\',\'' + \
            str(data['light']) + '\',\'' + \
            str(data['endpointid']) + '\')'
        if i != size - 1:
            sql = sql + ','

    return sql


# 接收手持机发送的信息
@csrf_exempt
@api_view(['POST'])
def nextsite(request):
    log.debug('receive request body:' + request.body)
    token = request.META.get('HTTP_TOKEN')
    if token is None or token != 'a921a69a33ae461396167d112b813d90':
        return JsonResponse(organize_result("False", "999999", "Unauthorized", {}),
                            status=status.HTTP_401_UNAUTHORIZED, safe=True)
    parameter = JSONParser().parse(request)
    tid = parameter['tid']
    site_code = parameter['site_code']
    latitude = parameter['latitude']
    longitude = parameter['longitude']
    # 货物进入或离开堆场状态
    # status = parameter['status']

    # 获取该云箱的起始堆场和目的地堆场的编号
    sql_1 = 'select box_order_relation.deviceid, ' \
            'site_info.location as s_site_name, ' \
            'site_info.latitude as s_latitude, ' \
            'site_info.longitude as s_longitude, ' \
            'site_info.site_code as s_site_code, ' \
            'site_info_2.location as d_site_name, ' \
            'site_info_2.latitude as d_latitude, ' \
            'site_info_2.longitude as d_longitude, ' \
            'site_info_2.site_code as d_site_code ' \
            'from iot.box_order_relation box_order_relation ' \
            'inner join iot.order_info order_info ' \
            'on box_order_relation.trackid = order_info.trackid ' \
            'inner join iot.site_info site_info ' \
            'on site_info.id = order_info.srcid ' \
            'inner join iot.site_info site_info_2 ' \
            'on site_info_2.id = order_info.dstid ' \
            'inner join iot.box_info box_info ' \
            'on box_info.deviceid = box_order_relation.deviceid ' \
            'and box_info.tid = \'' + tid + '\''
    data = query_list(sql_1)
    if len(data) > 0:
        s_site_code = data[0][4]
        d_site_code = data[0][8]

        # 获取该云箱运行所经过的堆场list
        sql_2 = 'select detail.order_id,' \
                'detail.site_code, site_info.latitude, site_info.longitude ' \
                'from iot.path_template template ' \
                'inner join iot.path_detail detail ' \
                'on template.template_id = detail.template_id ' \
                'inner join iot.site_info site_info ' \
                'on site_info.site_code = detail.site_code ' \
                'and template.s_site_code = \'' + s_site_code + '\'' \
                'and template.d_site_code = \'' + d_site_code + '\'' \
                'order by order_id asc'
        site_data = query_list(sql_2)
        next_site_code = cal_next_site(latitude, longitude, site_data)
        # 获取云箱内货物的类型与优先级（目前写死测试数据，等订单相关内容确定后，再从数据库中补齐）
        type = '0'  # 易碎物品类，编码见文档
        priority = '1'  # 优先级：次日达

        if site_code == '':
            t = {'S': s_site_code, 'D': d_site_code, 'N': next_site_code, 'type': type, 'priority': priority}
        else:
            t = {'N': next_site_code, 'type': type, 'priority': priority}
        return JsonResponse(organize_result("True", "000000", "Success", t), safe=True)
    else:
        # 该箱没有在途中
        return JsonResponse(organize_result("False", "999999", "Fail", 'Not on the way'), safe=True)


# 给定经纬度，计算该点在航线list中下一站
def cal_next_site(latitude, longitude, site_list):
    length = len(site_list)
    start_latitude = site_list[0][2]
    start_longitude = site_list[0][3]
    end_latitude = site_list[length-1][2]
    end_longitude = site_list[length-1][3]
    # 判断是否已经到达终点堆场，如果当前位置距离终点位置小于3000米，认为到达终点
    if get_distance(latitude, longitude, end_latitude, end_longitude) < 3000:
        return ''

    distance_list = []
    for i in range(length):
        distance_list.append(
            {'site_code': site_list[i][1],
             'distance': get_distance(start_latitude, start_longitude, site_list[i][2], site_list[i][3])})

    current_point = {'site_code': 'NA', 'distance': get_distance(start_latitude, start_longitude,
                                                                 cal_position(latitude), cal_position(longitude))}
    distance_list.append(current_point)
    sorted_list = sorted(distance_list, key=itemgetter('distance'))
    position = 0
    for j in range(len(sorted_list)):
        if sorted_list[j]['site_code'] == 'NA':
            break
        position = position + 1
    if len(sorted_list) == position + 1:
        return sorted_list[position - 1]['site_code']
    else:
        return sorted_list[position + 1]['site_code']


# 接收万引力公司传感器的信息
@csrf_exempt
@api_view(['POST'])
def save_precintl_data(request):
    token = request.META.get('HTTP_TOKEN')
    if token is None or token != 'a921a69a33ae461396167d112b813d90':
        return JsonResponse(organize_result("False", "999999", "Unauthorized", {}),
                            status=status.HTTP_401_UNAUTHORIZED, safe=True)
    if request.method == 'POST' or request.method == 'PUT':
        try:
            log.debug('receive request body:' + request.body)
            parameter = JSONParser().parse(request)
            sql = build_precintl_sql(parameter)
            save_to_db(sql)
            log.info('insert data to database successfully')
            return JsonResponse(organize_result("True", "000000", "OK", '{}'), status=status.HTTP_200_OK, safe=True)
        except Exception, e:
            log.error('save to db error, msg: ' + repr(e))
            return JsonResponse(organize_result("False", "999999", repr(e), '{}'),
                                status=status.HTTP_400_BAD_REQUEST, safe=True)
    else:
        msg = 'bad request method. please use POST/PUT.'
        log.error(msg)
        return JsonResponse(organize_result("False", "999999", msg, '{}'),
                            status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=True)


# 构建万引力数据插入数据库的sql
def build_precintl_sql(data):
    deviceid = str(data['deviceid'])
    lat = str(data['latitude'])
    long = str(data['longitude'])
    timestamp = str(data['utc'])
    speed = str(data['speed'])
    if speed == '0':
        speed = get_speed(deviceid, lat, long, timestamp)

    if lat == '0' or long == '0':
        location_data = get_location(deviceid, lat, long)
        lat = location_data['lat']
        long = location_data['long']

    sql = 'insert into iot.monservice_sensordata(timestamp, deviceid, temperature, humidity, latitude, longitude, ' \
          'speed, collide, light, endpointid) values '
    sql = sql + '(' + str(data['utc']) + ',\'' + \
                str(data['deviceid']) + '\',\'' + \
                str(data['temp']) + '\',\'' + \
                str(data['humi']) + '\',\'' + \
                str(lat) + '\',\'' + \
                str(long) + '\',\'' + \
                str(speed) + '\',\'' + \
                str(data['collide']) + '\',\'' + \
                str(data['light']) + '\',\'' + \
                str(data['deviceid']) + '\')'
    if str(data['deviceid']) == '' or str(data['temp']) == '' or str(data['humi']) == '' or \
       str(data['latitude']) == '' or str(data['longitude']) == '' or str(data['speed']) == '' or \
       str(data['collide']) == ''or str(data['light']) == '':
        return 'select 1'

    return sql


# 根据历史坐标计算平均速度
def get_speed(deviceid, lat, long, ts):
    try:
        last_data = query_list('select longitude,latitude,timestamp '
                                 'from iot.monservice_sensordata where deviceid = \'' + deviceid + '\' and longitude <> \'0\' and latitude <> \'0\' order by timestamp desc limit 2')

        if lat == '0' and long == '0':
            if len(last_data) == 2:
                start_latitude = last_data[0][1]
                start_longitude = last_data[0][0]
                end_latitude = last_data[1][1]
                end_longitude = last_data[1][0]
                start_time = last_data[0][2]
                end_time = last_data[1][2]
                speed = cal_speed(cal_position(start_latitude), cal_position(start_longitude), cal_position(end_latitude), cal_position(end_longitude), start_time, end_time)
                return speed
            else:
                return 0
        else:
            if len(last_data) > 0:
                start_latitude = lat
                start_longitude = long
                end_latitude = last_data[0][1]
                end_longitude = last_data[0][0]
                start_time = ts
                end_time = last_data[0][2]
                speed = cal_speed(cal_position(start_latitude), cal_position(start_longitude), cal_position(end_latitude), cal_position(end_longitude), start_time, end_time)
                return speed
            else:
                return 0
    except Exception, e:
        log.error('get_speed error:' + e.message)
        return 0


# 如果上报的经纬度是0，则以最后一次不是0的值替代
def get_location(deviceid, lat, long):
    last_lat = '0'
    last_long = '0'
    last_data = query_list('select latitude, longitude '
                           'from iot.monservice_sensordata where deviceid = \'' + deviceid + '\' and longitude <> \'0\' and latitude <> \'0\' order by timestamp desc limit 1')

    if len(last_data) > 0:
        last_lat = last_data[0][0]
        last_long = last_data[0][1]

    return {'lat': last_lat, 'long': last_long}


# 获取获取每日导出的数据
@csrf_exempt
@api_view(['GET'])
def get_data(request):
    try:
        today = str(time.strftime('%Y-%m-%d', time.localtime(int(time.time()))))
        day = request.GET.get('day')
        if day == '':
            end_time_str = today + ' 00:00:00'
            end_time = int(time.mktime(time.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')))
        else:
            end_time = int(time.mktime(time.strptime(day, '%Y-%m-%d'))) + 3600 * 24

    except Exception, e:
        log.error(e.message)
        return JsonResponse(organize_result("False", "999999", "parameter is required", '{}'),
                            status=status.HTTP_400_BAD_REQUEST, safe=True)

    start_time = end_time - 3600 * 24
    save_path = '/opt/pg-data/dump_data/'
    zip_file_name = 'sensor_data_' + time.strftime('%Y-%m-%d', time.localtime(start_time)) + '.zip'
    download_file_name = save_path + zip_file_name
    if os.path.exists(download_file_name):
        def file_iterator(file_name, chunk_size=512):
            with open(file_name) as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(download_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(zip_file_name)

        return response
    else:
        return JsonResponse(organize_result("False", "999999", 'File dose not exists', '{}'),
                            status=status.HTTP_400_BAD_REQUEST, safe=True)


# 导出前一天的传感器数据
@csrf_exempt
@api_view(['GET'])
def dump_data(request):
    try:
        today = str(time.strftime('%Y-%m-%d', time.localtime(int(time.time()))))
        day = request.GET.get('day')
        if day == '':
            end_time_str = today + ' 00:00:00'
            end_time = int(time.mktime(time.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')))
        else:
            end_time = int(time.mktime(time.strptime(day, '%Y-%m-%d'))) + 3600 * 24

    except Exception, e:
        log.error(e.message)
        return JsonResponse(organize_result("False", "999999", "parameter is required", '{}'),
                            status=status.HTTP_400_BAD_REQUEST, safe=True)
    try:
        log.info("dump sensor data begin ...")
        start_time = end_time - 3600 * 24

        txt_file_name = 'sensor_data_' + time.strftime('%Y-%m-%d', time.localtime(start_time)) + '.txt'
        zip_file_name = 'sensor_data_' + time.strftime('%Y-%m-%d', time.localtime(start_time)) + '.zip'
        save_path = '/opt/pg-data/dump_data/'
        full_name = save_path + txt_file_name
        SensorData.objects.\
            filter(timestamp__gte=start_time, timestamp__lt=end_time).to_csv(full_name)
        log.info("dump sensor data finish, file_name:" + full_name)
        if os.path.exists(full_name):
            f = zipfile.ZipFile(save_path + zip_file_name, 'w', zipfile.ZIP_DEFLATED)
            f.write(full_name, txt_file_name)
            f.close()
            log.info("zip file finish, zip file name:" + zip_file_name)
            os.remove(full_name)
            log.info("remove file finish, file_name:" + full_name)
        else:
            log.error("dump sensor data error, file_name:" + full_name)
    except Exception, e:
        log.error('dump sensor data error, msg:' + e.message)
        return JsonResponse(organize_result("False", "999999", 'ERROR', '{}'),
                            status=status.HTTP_400_BAD_REQUEST, safe=True)

    return JsonResponse(organize_result("True", "000000", 'OK', '{}'),
                        status=status.HTTP_200_OK, safe=True)
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from util.db import save_to_db, query_list
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
# Create your views here.
from rest_framework import status
from util import logger
from operator import itemgetter
import math
from sensor.errcode import *


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
            return JsonResponse(RESULT_200_OK, status=status.HTTP_200_OK)
        except Exception, e:
            log.error('save to db error, msg: ' + e.__str__())
            return JsonResponse(RESULT_400_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)
    else:
        log.error('bad request method. please use POST/PUT.')
        return JsonResponse(RESULT_400_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)


# 解析数据
def parse(msg):
    body = json.loads(str(msg))
    s = body['data']
    meta = body['meta']
    deviceid = str(s['device_id'])
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
    sql = 'insert into iot.sensor_data(timestamp, deviceid, temperature, humidity, latitude, longitude, ' \
          'speed, collide, light, endpointid) values '
    size = data_list.__len__()

    for i in range(size):
        data = data_list[i]
        sql = sql + '(\'' + str(data['timestamp']) + '\',\'' + \
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
    token = request.META.get('HTTP_TOKEN')
    if token is None or token != 'a921a69a33ae461396167d112b813d90':
        return JsonResponse(organize_result("False", "999999", "Unauthorized", {}),
                            status=status.HTTP_401_UNAUTHORIZED)
    parameter = JSONParser().parse(request)
    tid = parameter['tid']
    site_code = parameter['site_code']
    latitude = parameter['latitude']
    longitude = parameter['longitude']

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

        if site_code == '':
            t = {'S': s_site_code, 'D': d_site_code, 'N': next_site_code}
        else:
            t = {'N': next_site_code}
        return JsonResponse(organize_result("True", "000000", "Success", t))
    else:
        # 该箱没有在途中
        return JsonResponse(organize_result("False", "999999", "Fail", 'Not on the way'))


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
                            status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST' or request.method == 'PUT':
        try:
            log.debug('receive request body:' + request.body)
            parameter = JSONParser().parse(request)
            sql = build_precintl_sql(parameter)
            save_to_db(sql)
            log.info('insert data to database successfully')
            return JsonResponse({'msg': 200}, status=status.HTTP_200_OK)
        except Exception, e:
            log.error('save to db error, msg: ' + repr(e))
            return JsonResponse({'msg': repr(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        msg = 'bad request method. please use POST/PUT.'
        log.error(msg)
        return JsonResponse({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)


# 构建万引力数据插入数据库的sql
def build_precintl_sql(data):
    sql = 'insert into iot.sensor_data(timestamp, deviceid, temperature, humidity, latitude, longitude, ' \
          'speed, collide, light) values '
    sql = sql + '(' + str(data['utc']) + ',\'' + \
                str(data['deviceid']) + '\',\'' + \
                str(data['temp']) + '\',\'' + \
                str(data['humi']) + '\',\'' + \
                str(data['latitude']) + '\',\'' + \
                str(data['longitude']) + '\',\'' + \
                str(data['speed']) + '\',\'' + \
                str(data['collide']) + '\',\'' + \
                str(data['light']) + '\')'
    return sql


# 将传感器数据的经度或纬度转换为小数点形式，Longitude: 116296046, //dddmmmmmm   Latitude: 39583032,  //ddmmmmmm
def cal_position(value):
    hour = value[:-6]
    minute = value[len(hour):len(value)]

    return float(hour + '.' + minute)


# 获取两点之间的距离
def get_distance(start_latitude, start_longitude, end_latitude, end_longitude):
    lat1 = (math.pi / 180) * float(start_latitude)
    lat2 = (math.pi / 180) * float(end_latitude)
    lon1 = (math.pi / 180) * float(start_longitude)
    lon2 = (math.pi / 180) * float(end_longitude)
    # 地球半径
    r = 6371
    d = math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lon2-lon1))*r
    # 单位米
    return d*1000











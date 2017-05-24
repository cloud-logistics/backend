#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from util.db import save_to_db
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from rest_framework import status
from util import logger


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
    deviceid = str(s['device_id'])
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
                                  'speed': speed, 'collide': collide, 'light': light}]

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
                              'speed': speed, 'collide': collide, 'light': light}]

            else:
                log.error('legacy format error, legacy: ' + legacy)

    return data_list


def build_sql(data_list):
    sql = 'insert into iot.sensor_data(timestamp, deviceid, temperature, humidity, latitude, longitude, ' \
          'speed, collide, light) values '
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
            str(data['light']) + '\')'
        if i != size - 1:
            sql = sql + ','

    return sql

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logger
import json
import psycopg2
from psycopg2.pool import ThreadedConnectionPool


# logging
log = logger.get_logger('db')


def save_to_db(msg):
    data_list = parse(msg)

    pool = ThreadedConnectionPool(
        minconn=5,
        maxconn=20,
        database="cloudbox",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )
    conn = pool.getconn()
    cur = conn.cursor()
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

    log.debug('sql: ' + sql)
    cur.execute(sql)
    cur.close()
    conn.commit()
    pool.putconn(conn)


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

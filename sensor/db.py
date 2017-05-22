#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logger
import json
import psycopg2
from psycopg2.pool import ThreadedConnectionPool


# logging
log = logger.get_logger('db')


def save_to_db(msg):
    data = parse(msg)

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
          'speed, collide, light, legacy) ' \
          'values (\'' + str(data['timestamp']) + '\',\'' + \
          str(data['deviceid']) + '\',\'' +\
          str(data['temperature']) + '\',\'' + \
          str(data['humidity']) + '\',\'' + \
          str(data['latitude']) + '\',\'' + \
          str(data['longitude']) + '\',\'' + \
          str(data['speed']) + '\',\'' + \
          str(data['collide']) + '\',\'' + \
          str(data['light']) + '\',\'' + \
          str(data['legacy']) + '\')'
    log.debug('sql: ' + sql)
    cur.execute(sql)
    cur.close()
    conn.commit()
    pool.putconn(conn)


def parse(msg):
    body = json.loads(str(msg))
    s = body['data']
    timestamp = s['utc']
    deviceid = s['device_id']
    temperature = s['temp']
    humidity = s['humi']
    latitude = s['latitude']
    longitude = s['longitude']
    speed = s['speed']
    collide = s['collide']
    light = s['light']
    legacy = s['legacy']

    return {'timestamp': timestamp, 'deviceid': deviceid,
            'temperature': temperature, 'humidity': humidity,
            'latitude': latitude, 'longitude': longitude,
            'speed': speed, 'collide': collide, 'light': light,
            'legacy': legacy}

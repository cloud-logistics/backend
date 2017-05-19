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
        password="root",
        host="127.0.0.1",
        port="5432"
    )
    conn = pool.getconn()
    cur = conn.cursor()
    sql = 'insert into iot.sensor_data(timestamp, clientid, temperature, humidity, latitude, longitude) ' \
          'values (\'' + str(data['timestamp']) + '\',\'' + \
          str(data['clientid']) + '\',\'' +\
          str(data['temperature']) + '\',\'' + \
          str(data['humidity']) + '\',\'' + \
          str(data['latitude']) + '\',\'' + \
          str(data['longitude']) + '\')'
    log.debug('sql: ' + sql)
    cur.execute(sql)
    cur.close()
    conn.commit()
    pool.putconn(conn)


def parse(msg):
    s = json.loads(str(msg))
    data = s['datastreams']
    timestamp = ''
    clientid = ''
    temperature = ''
    humidity = ''
    latitude = ''
    longitude = ''

    for element in data:
        if element.has_key('Time_UTC'):
            timestamp = element['Time_UTC']

        if element.has_key('ClientId'):
            clientid = element['ClientId']

        if element.has_key('id') and element['id'] == 'TempHumi':
            temperature = element['datapoints'][0]['Temperature']
            humidity = element['datapoints'][0]['Humidity']

        if element.has_key('id') and element['id'] == 'GPS':
            latitude = element['datapoints'][0]['Latitude']
            longitude = element['datapoints'][0]['Longitude']

    return {'timestamp': timestamp, 'clientid': clientid,
            'temperature': temperature, 'humidity': humidity,
            'latitude': latitude, 'longitude': longitude}

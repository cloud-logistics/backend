#! /usr/bin/env python
# -*- coding: utf-8 -*-


import math
import json
import urllib
import urllib2
from util import logger

log = logger.get_logger(__name__)


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


# 计算速度(公里/小时)
def cal_speed(start_latitude, start_longitude, end_latitude, end_longitude, start_time, end_time):
    distance = get_distance(start_latitude, start_longitude, end_latitude, end_longitude)
    time_span = int(start_time) - int(end_time)
    if time_span > 0:
        speed = 3.6 * distance / time_span
        return speed
    else:
        return 0


# 将传感器数据的经度或纬度转换为小数点形式，Longitude: 116296046, //dddmmmmmm   Latitude: 39583032,  //ddmmmmmm
def cal_position(value):
    if len(value) > 6:
        hour = value[:-6]
        minute = value[len(hour):len(value)]
        return float(hour + '.' + minute)
    else:
        return value

# 根据地点名称获取经纬度
def get_lng_lat(address):
    lng = 0
    lat = 0
    values = {}
    values['address'] = address
    values['key'] = "AIzaSyBeNmcjCubIBu3xusqOtQxqdn1EkXTk50M"
    params = urllib.urlencode(values)
    url = "https://ditu.google.cn/maps/api/geocode/json"
    geturl = url + "?" + params
    request = urllib2.Request(geturl)
    response = urllib2.urlopen(request)
    response_dic = json.loads(response.read())

    if response_dic['status'] == 'OK':
        lng = response_dic['results'][0]['geometry']['location']['lng']
        lat = response_dic['results'][0]['geometry']['location']['lat']
    else:
        log.info("req response: %s" % response_dic)

    return {'lng': lng, 'lat': lat}


# 根据两个地点名称获取之间的距离
def get_path_distance(origin, destination):
    values = {}
    values['language'] = 'zh-CN'
    values['origin'] = origin
    values['destination'] = destination
    values['key'] = "AIzaSyBeNmcjCubIBu3xusqOtQxqdn1EkXTk50M"
    params = urllib.urlencode(values)
    url = "https://ditu.google.cn/maps/api/directions/json"
    geturl = url + "?" + params
    request = urllib2.Request(geturl)
    response = urllib2.urlopen(request)
    response_dic = json.loads(response.read())

    if response_dic['status'] == 'OK':
        distance = response_dic['routes'][0]['legs'][0]['distance']['value']
    else:
        log.info("req response: %s" % response_dic)
        return 0
    return distance





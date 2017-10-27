#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.settings import api_settings
from monservice.models import SiteInfo
from monservice.serializers import SiteInfoSerializer
from rentservice.utils.retcode import *
from rentservice.utils.logger import *
import uuid
import datetime
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')


# 根据GPS定位信息获取距离最近的堆场
@csrf_exempt
@api_view(['GET'])
def get_site_list(request, latitude, longitude):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    _lat = float(latitude)
    _lng = float(longitude)
    site_list = SiteInfo.objects.raw(
        '''select *, ROUND(6378.138*2*ASIN(SQRT(POW(SIN((%s*PI()/180-latitude::NUMERIC *PI()/180)/2),2) \
        +COS(%s*PI()/180)*COS(latitude::NUMERIC*PI()/180)*POW(SIN((%s*PI()/180-longitude::NUMERIC*PI()/180)/2),2)))*1000) AS juli\
        from monservice_siteinfo order by juli ASC
        ''', [_lat, _lat, _lng])
    res_site = []
    for item in site_list:
        res_site.append(
            {'id': item.id, 'location': item.location, 'latitude': item.latitude, 'longitude': item.longitude,
             'site_code': item.site_code, 'city': item.city, 'nation': item.nation, 'province': item.province})
    page = paginator.paginate_queryset(res_site, request)
    ret_ser = SiteInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 根据省市查询堆场列表
@csrf_exempt
@api_view(['GET'])
def get_site_by_province(request, province, city):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    _province = int(province)
    _city = int(city)
    if _province == 0 and _city == 0:
        print 'all'
        site_list = SiteInfo.objects.all().order_by('id')
    elif _province != 0 and _city == 0:
        print 'province'
        site_list = SiteInfo.objects.filter(province=_province).order_by('id')
    elif _province != 0 and _city != 0:
        print 'city'
        site_list = SiteInfo.objects.filter(city=_city).order_by('id')
    page = paginator.paginate_queryset(site_list, request)
    ret_ser = SiteInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)

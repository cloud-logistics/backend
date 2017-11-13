#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.settings import api_settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rentservice.utils.retcode import *
from django.db import transaction
from monservice.models import BoxInfo
from monservice.models import Province
from monservice.models import City
from monservice.models import SiteInfo
from rentservice.serializers import BoxInfoSerializer
from django.conf import settings
import datetime
import uuid
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


# 云箱list查询（condition：province_id,city_id,site_id,ava_flag）
@csrf_exempt
@api_view(['POST'])
def get_box_info_list(request):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    data = JSONParser().parse(request)
    try:
        province_id = data['province_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "province输入有误"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        city_id = data['city_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "city输入有误"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        site_id = data['site_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "site输入有误"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        ava_flag = data['ava_flag']
    except Exception:
        return JsonResponse(retcode({}, "9999", "可用标志输入有误"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    query_set = BoxInfo.objects
    if province_id != 0:
        try:
            province = Province.objects.get(province_id=province_id)
        except Province.DoesNotExist:
            return JsonResponse(retcode({}, "9999", "省信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        query_set = query_set.filter(siteinfo__province=province)
    if city_id != 0:
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse(retcode({}, "9999", "市信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        query_set = query_set.filter(siteinfo__city=city)
    if site_id != 0:
        try:
            site = SiteInfo.objects.get(id=site_id)
        except SiteInfo.DoesNotExist:
            return JsonResponse(retcode({}, "9999", "仓库信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        query_set = query_set.filter(siteinfo=site)
    if ava_flag != '':
        query_set = query_set.filter(ava_flag=ava_flag)
    page = paginator.paginate_queryset(query_set, request)
    ret_ser = BoxInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


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
from rentservice.serializers import BoxInfoListSerializer
from rentservice.serializers import BoxInfoResSerializer
from rentservice.models import RentLeaseInfo
from rentservice.serializers import RentLeaseBoxSerializer
from django.conf import settings
from monservice.models import SensorData
from monservice.serializers import SensorPathDataSerializer
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
    param = request.query_params
    if param:
        pagination_class.default_limit = int(param.get('limit'))
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
    try:
        box_id = data['box_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "云箱id输入有误"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    query_set = BoxInfo.objects
    condition = 'N'
    if province_id != 0:
        try:
            province = Province.objects.get(province_id=province_id)
        except Province.DoesNotExist:
            return JsonResponse(retcode({}, "9999", "省信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        query_set = query_set.filter(siteinfo__province=province)
        condition = 'Y'
    if city_id != 0:
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse(retcode({}, "9999", "市信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        query_set = query_set.filter(siteinfo__city=city)
        condition = 'Y'
    if site_id != 0:
        try:
            site = SiteInfo.objects.get(id=site_id)
        except SiteInfo.DoesNotExist:
            return JsonResponse(retcode({}, "9999", "仓库信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        query_set = query_set.filter(siteinfo=site)
        condition = 'Y'
    if ava_flag != '':
        query_set = query_set.filter(ava_flag=ava_flag)
        condition = 'Y'
    if box_id != '':
        query_set = query_set.filter(deviceid__contains=box_id)
        condition = 'Y'
    if condition == 'N':
        query_set = query_set.all()
    page = paginator.paginate_queryset(query_set, request)
    ret_ser = BoxInfoListSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['GET'])
def get_box_detail(request, box_id):
    try:
        box_info = BoxInfo.objects.get(deviceid=box_id)
    except BoxInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "云箱不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    sensor_data = SensorData.objects.filter(deviceid=box_id).order_by('-timestamp')
    if len(sensor_data) > 0:
        last_data = sensor_data[0]
        _location = SensorPathDataSerializer(last_data).data
    else:
        _sensor = SensorData(deviceid=box_id, timestamp=0, latitude='0', longitude='0')
        _location = SensorPathDataSerializer(_sensor).data

    return JsonResponse(retcode(
        {'box_info': BoxInfoResSerializer(box_info).data, 'location': _location},
        "0000", "Success"), safe=True,
        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_box_stat(request, box_id):
    try:
        box = BoxInfo.objects.get(deviceid=box_id)
    except BoxInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "云箱不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # 获取周区间
    today = datetime.datetime.today()
    week_start_tmp = today - datetime.timedelta(days=today.weekday())
    week_start = datetime.datetime(week_start_tmp.year,week_start_tmp.month, week_start_tmp.day, 0, 0, 0)
    week_end = today + datetime.timedelta(days=7 - today.weekday())
    week_queryset = RentLeaseInfo.objects.filter(rent_status=1, lease_start_time__gte=week_start,
                                                 lease_start_time__lte=week_end, box=box)
    week_count = week_queryset.count()
    week_time = 0
    for week in week_queryset:
        if week.lease_start_time is not None and week.lease_end_time is not None:
            week_time += float((week.lease_end_time - week.lease_start_time).days) * 24 + float(
                (week.lease_end_time - week.lease_start_time).seconds) / 3600
    # 获取月区间
    y = today.year
    m = today.month
    month_start_dt = datetime.date(y, m, 1)
    if m == 12:
        month_end_dt = datetime.date(y + 1, 1, 1)
        # month_end_dt = datetime.date(y + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        month_end_dt = datetime.date(y, m + 1, 1)
        # month_end_dt = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
    month_queryset = RentLeaseInfo.objects.filter(rent_status=1, lease_start_time__gte=month_start_dt,
                                                  lease_start_time__lte=month_end_dt, box=box)
    month_count = month_queryset.count()
    month_time = 0
    for month in month_queryset:
        if month.lease_start_time is not None and month.lease_end_time is not None:
            month_time += float((month.lease_end_time - month.lease_start_time).days) * 24 + float(
                (month.lease_end_time - month.lease_start_time).seconds) / 3600
    # 获取年区间
    year_start = datetime.date(y, 1, 1)
    year_end = datetime.date(y + 1, 1, 1)
    year_queryset = RentLeaseInfo.objects.filter(rent_status=1, lease_start_time__gte=year_start,
                                                 lease_start_time__lte=year_end, box=box)
    year_count = year_queryset.count()
    year_time = 0
    for year in year_queryset:
        if year.lease_start_time is not None and year.lease_end_time is not None:
            year_time += float((year.lease_end_time - year.lease_start_time).days) * 24 + float(
                (year.lease_end_time - year.lease_start_time).seconds) / 3600
    ret = {'week_count': week_count, 'week_time': week_time, 'month_count': month_count, 'month_time': month_time,
           'year_count': year_count, 'year_time': year_time}
    return JsonResponse(retcode(ret, '0000', 'Success'), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_box_lease_list(request, box_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        box = BoxInfo.objects.get(deviceid=box_id)
    except BoxInfo.DoesNotExist:
        return JsonResponse(retcode({}, '9999', '云箱信息不存在'), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    lease_list = RentLeaseInfo.objects.filter(box=box).order_by('-lease_start_time')
    page = paginator.paginate_queryset(lease_list, request)
    ret_ser = RentLeaseBoxSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)

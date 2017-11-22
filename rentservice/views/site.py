#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rest_framework.parsers import JSONParser
from django.db.models import Q
from monservice.models import SiteInfo
from monservice.models import BoxTypeInfo
from monservice.models import BoxInfo
from monservice.serializers import SiteInfoSerializer
from monservice.serializers import BoxTypeInfoSerializer
from rentservice.utils.retcode import *
from monservice.models import SiteBoxStock
from monservice.serializers import SiteBoxStockSerializer
from monservice.serializers import SiteInfoMoreSerializer
from rentservice.models import SiteStat
from rentservice.models import SiteStatDetail
from rentservice.serializers import SiteStatResSerializer
from rentservice.serializers import AllSiteSerializer
import pytz
from django.conf import settings

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


# 根据GPS定位信息获取附近20公里内的仓库
@csrf_exempt
@api_view(['GET'])
def get_site_list_nearby(request, latitude, longitude):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    _lat = float(latitude)
    _lng = float(longitude)
    site_list = SiteInfo.objects.raw(
        '''select t2.* from (select *, ROUND(6378.138*2*ASIN(SQRT(POW(SIN((%s*PI()/180-latitude::NUMERIC *PI()/180)/2),2) \
        +COS(%s*PI()/180)*COS(latitude::NUMERIC*PI()/180)*POW(SIN((%s*PI()/180-longitude::NUMERIC*PI()/180)/2),2)))) AS juli\
        from monservice_siteinfo order by juli ASC) as t2 where t2.juli < 20
        ''', [_lat, _lat, _lng])
    res_site = []
    for item in site_list:
        # 获取每个堆场的各箱子类型的数量
        site_box_num = SiteBoxStock.objects.filter(site=item)
        res_site.append(
            {'id': item.id, 'location': item.location, 'latitude': item.latitude, 'longitude': item.longitude,
             'site_code': item.site_code, 'city': item.city, 'nation': item.nation, 'province': item.province,
             'name': item.name,
             'box_num': site_box_num})
    page = paginator.paginate_queryset(res_site, request)
    ret_ser = SiteInfoMoreSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


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
        +COS(%s*PI()/180)*COS(latitude::NUMERIC*PI()/180)*POW(SIN((%s*PI()/180-longitude::NUMERIC*PI()/180)/2),2)))) AS juli\
        from monservice_siteinfo order by juli ASC
        ''', [_lat, _lat, _lng])
    res_site = []
    for item in site_list:
        # 获取每个堆场的各箱子类型的数量
        site_box_num = SiteBoxStock.objects.filter(site=item)
        res_site.append(
            {'id': item.id, 'location': item.location, 'latitude': item.latitude, 'longitude': item.longitude,
             'site_code': item.site_code, 'city': item.city, 'nation': item.nation, 'province': item.province,
             'name': item.name,
             'box_num': site_box_num})
    page = paginator.paginate_queryset(res_site, request)
    ret_ser = SiteInfoMoreSerializer(page, many=True)
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
        site_list = SiteInfo.objects.all().order_by('id')
    elif _province != 0 and _city == 0:
        site_list = SiteInfo.objects.filter(province=_province).order_by('id')
    elif _province != 0 and _city != 0:
        site_list = SiteInfo.objects.filter(city=_city).order_by('id')
    res_site = []
    for item in site_list:
        # 获取每个堆场的各箱子类型的数目
        site_box_num = SiteBoxStock.objects.filter(site=item)
        res_site.append(
            {'id': item.id, 'location': item.location, 'latitude': item.latitude, 'longitude': item.longitude,
             'site_code': item.site_code, 'city': item.city, 'nation': item.nation, 'province': item.province,
             'name': item.name,
             'box_num': site_box_num})
    page = paginator.paginate_queryset(res_site, request)
    ret_ser = SiteInfoMoreSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 查询堆场的详细信息，包括每种类型的箱子所剩下可租用的个数
@csrf_exempt
@api_view(['GET'])
def get_site_detail(request, site_id):
    try:
        site_info = SiteInfo.objects.get(id=site_id)
    except SiteInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "堆场信息不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取各种类型箱子的可用个数
    box_num = SiteBoxStock.objects.filter(site=site_info)
    return JsonResponse(
        retcode(
            {'site_info': SiteInfoSerializer(site_info).data,
             'box_counts': SiteBoxStockSerializer(box_num, many=True).data},
            "0000", "Success"),
        safe=True,
        status=status.HTTP_200_OK)


# 获取堆场的统计信息
@csrf_exempt
@api_view(['GET'])
def get_site_stat(request, site_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        site = SiteInfo.objects.get(id=site_id)
    except SiteInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "仓库信息不存在"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    stat_list = SiteStat.objects.filter(site=site).order_by('-stat_day')
    print stat_list
    res_stat = []
    for stat_item in stat_list:
        details = SiteStatDetail.objects.filter(sitestat=stat_item)
        res_stat.append({'stat_id': stat_item.stat_id, 'stat_day': stat_item.stat_day, 'total_in': stat_item.total_in,
                         'total_out': stat_item.total_out, 'site': stat_item.site, 'detail': details})
    page = paginator.paginate_queryset(res_stat, request)
    ret_ser = SiteStatResSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['GET'])
def get_all_site(request):
    site_list = SiteInfo.objects.all()
    return JsonResponse(retcode(AllSiteSerializer(site_list, many=True).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def get_site_by_filter(request):
    data = JSONParser().parse(request)
    try:
        site_name = data['site_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", "仓库参数必输"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    param = request.query_params
    if param:
        pagination_class.default_limit = int(param.get('limit'))
    paginator = pagination_class()
    site_list = SiteInfo.objects.filter(Q(name__contains=site_name) | Q(location__contains=site_name))
    page = paginator.paginate_queryset(site_list, request)
    ret_ser = SiteInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)

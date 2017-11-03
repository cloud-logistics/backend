#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.serializers import SiteFullInfoSerializer, BoxFullInfoSerializer
import json
from monservice.models import SiteInfo, City, Province, Nation, BoxTypeInfo, BoxInfo
from util import logger
from rest_framework.settings import api_settings

log = logger.get_logger('monservice.site.py')

# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


# 新增堆场
@csrf_exempt
@api_view(['POST'])
def add_site(request):
    try:
        data = json.loads(request.body)
        location = to_str(data['location'])             # 堆场名称
        longtitude = to_str(data['longitude'])          # 经度
        latitude = to_str(data['latitude'])             # 纬度
        site_code = to_str(data['site_code'])           # 堆场代码
        volume = data['volume']                 # 堆场箱子容量
        city_id = data['city_id']                       # 城市
        province_id = data['province_id']               # 省
        nation_id = data['nation_id']                   # 国家

        city = City.objects.get(id=city_id)
        province = Province.objects.get(province_id=province_id)
        nation = Nation.objects.get(nation_id=nation_id)
        site = SiteInfo(location=location, latitude=latitude, longitude=longtitude, site_code=site_code,
                        city= city, province=province, nation=nation, volume=volume)
        site.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'add site success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

# 删除堆场
@csrf_exempt
@api_view(['DELETE'])
def delete_site(request, id):
    try:
        SiteInfo.objects.get(id=id).delete()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'delete site success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 修改堆场
@csrf_exempt
@api_view(['PUT'])
def modify_site(request, id):
    try:
        data = json.loads(request.body)

        site = SiteInfo.objects.get(id=id)
        site.location = to_str(data['location'])  # 堆场名称
        site.longitude = to_str(data['longitude'])  # 经度
        site.latitude = to_str(data['latitude'])  # 纬度
        site.site_code = to_str(data['site_code'])  # 堆场代码
        site.volume = data['volume']  # 堆场箱子容量

        city_id = data['city_id']  # 城市
        province_id = data['province_id']  # 省
        nation_id = data['nation_id']  # 国家
        city = City.objects.get(id=city_id)
        province = Province.objects.get(province_id=province_id)
        nation = Nation.objects.get(nation_id=nation_id)
        site.city = city
        site.province = province
        site.nation = nation
        site.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'modify site success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 获取全部堆场信息
@csrf_exempt
@api_view(['GET'])
def get_sites(request):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        sites = SiteInfo.objects.all().order_by('id')
        page = paginator.paginate_queryset(sites, request)
        ret_ser = SiteFullInfoSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query sites success')


# 根据堆场ID获取堆场内的云箱
@csrf_exempt
@api_view(['GET'])
def get_site_boxes(request, id):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        boxes = BoxInfo.objects.filter(siteinfo_id=id).order_by('deviceid')
        page = paginator.paginate_queryset(boxes, request)
        ret_ser = BoxFullInfoSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query sites box success')




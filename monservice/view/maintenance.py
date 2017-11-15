#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.serializers import MaintenanceStationSerializer
import json
from monservice.models import MaintenanceStation
from util import logger
from rest_framework.settings import api_settings


log = logger.get_logger('monservice.maintenance.py')


# 新增维修点
@csrf_exempt
@api_view(['POST'])
def create_maintenance(request):
    try:
        data = json.loads(request.body)
        name = data['name']
        city_id = data['city_id']                       # 城市
        province_id = data['province_id']               # 省
        nation_id = data['nation_id']                   # 国家
        contact = data['contact']
        longitude = data['longitude']
        latitude = data['latitude']

        mainten = MaintenanceStation(name=name, latitude=latitude, longitude=longitude,
                        city_id= city_id, province_id=province_id, nation=nation_id, contact=contact)
        mainten.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'add maintenance station success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 删除维修地点
@csrf_exempt
@api_view(['DELETE'])
def delete_maintenance(request, maintenance_id):
    try:
        MaintenanceStation.objects.get(id=maintenance_id).delete()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'delete maintenance station success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 修改维修点
@csrf_exempt
@api_view(['PUT'])
def update_maintenance(request, maintenance_id):
    try:
        data = json.loads(request.body)
        ms = MaintenanceStation.objects.get(id=maintenance_id)
        ms.name = data['name']
        ms.city_id = data['city_id']  # 城市
        ms.province_id = data['province_id']  # 省
        ms.nation_id = data['nation_id']  # 国家
        ms.contact = data['contact']
        ms.longitude = data['longitude']
        ms.latitude = data['latitude']
        ms.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'update maintenance station success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 获取全部维修点信息
@csrf_exempt
@api_view(['GET'])
def get_maintenance(request):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        sites = MaintenanceStation.objects.all().order_by('id')
        page = paginator.paginate_queryset(sites, request)
        ret_ser = MaintenanceStationSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query maintenance station success')

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rentservice.utils.retcode import *
from monservice.models import Province
from monservice.models import City
from monservice.serializers import ProvinceSerializer
from monservice.serializers import CitySerializer
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')


# 获取省列表
@csrf_exempt
@api_view(['GET'])
def get_province_list(request):
    province_list = Province.objects.all().order_by('province_id')
    return JsonResponse(retcode(ProvinceSerializer(province_list, many=True).data, "000000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 获取市列表
@csrf_exempt
@api_view(['GET'])
def get_city_list(request, province_id):
    try:
        province = Province.objects.get(province_id=province_id)
    except Province.DoesNotExist:
        return JsonResponse(retcode({}, "999999", "省信息不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    city_list = City.objects.filter(province=province).order_by('id')
    return JsonResponse(retcode(CitySerializer(city_list, many=True).data, "000000", "Success"), safe=True,
                        status=status.HTTP_200_OK)

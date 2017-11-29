#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rentservice.utils.retcode import *
from rentservice.models import Param
from rentservice.serializers import ParamSerializer
from rest_framework.parsers import JSONParser

import pytz
from django.conf import settings

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['GET'])
def get_param(request, param_key):
    try:
        param = Param.objects.get(param_key=param_key)
    except Param.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "参数不存在"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode({}, "0000", "Success"), safe=True, status=status.HTTP_200_OK)


# set travel parameters
@csrf_exempt
@api_view(['POST'])
def set_param(request):
    data = JSONParser().parse(request)
    try:
        param = Param.objects.get(param_key=data['param_key'])
    except Param.DoesNotExist:
        param_insert = Param(param_key=data['param_key'], param_value=data['param_value'],
                             param_desc=data['param_desc'])
        param_insert.save()
        return JsonResponse(retcode(ParamSerializer(param_insert).data, "0000", "Success"),
                            safe=True, status=status.HTTP_201_CREATED)
    param.param_value = data['param_value']
    param.param_desc = data['param_desc']
    param.save()
    return JsonResponse(retcode(ParamSerializer(param).data, "0000", "Success"),
                        safe=True, status=status.HTTP_200_OK)

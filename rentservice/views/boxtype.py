#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.models import BoxTypeInfo
from monservice.serializers import BoxTypeInfoSerializer
from rentservice.utils.retcode import *
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')


# 获取箱子类型的接口
@csrf_exempt
@api_view(['GET'])
def get_box_type_list(request):
    type_list = BoxTypeInfo.objects.all()
    return JsonResponse(retcode(BoxTypeInfoSerializer(type_list, many=True).data, "000000", "Success"), safe=True,
                        status=status.HTTP_200_OK)

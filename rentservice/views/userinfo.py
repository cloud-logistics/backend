#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rentservice.utils.retcode import *
from rentservice.models import EnterpriseUser
from rentservice.models import RentLeaseInfo
from rentservice.serializers import RentLeaseInfoSerializer
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')


@csrf_exempt
@api_view(['GET'])
def get_process_order_list(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)

    # 获取正在运行中的箱子
    lease_list = RentLeaseInfo.objects.filter(on_site__isnull=True, user_id=user)
    page = paginator.paginate_queryset(lease_list, request)
    ret_ser = RentLeaseInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['GET'])
def get_finished_order_list(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)

    # 获取正在运行中的箱子
    lease_list = RentLeaseInfo.objects.filter(on_site__isnull=False, user_id=user)
    page = paginator.paginate_queryset(lease_list, request)
    ret_ser = RentLeaseInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)

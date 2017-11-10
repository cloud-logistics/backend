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
from django.conf import settings


log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


# 企业查询在运云箱订单
# enterprise_id实际传递值还是企业用户的user_id
@csrf_exempt
@api_view(['GET'])
def get_enterprise_lease_process_list(request, enterprise_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=enterprise_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "企业用户不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # 获取所有企业下所有用户的在运的订单
    process_list = RentLeaseInfo.objects.filter(on_site__isnull=True, user_id__enterprise=user.enterprise)
    page = paginator.paginate_queryset(process_list, request)
    ret_ser = RentLeaseInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 企业查询历史云箱订单
# enterprise_id实际传递值还是企业用户的user_id
@csrf_exempt
@api_view(['GET'])
def get_enterprise_lease_finish_list(request, enterprise_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=enterprise_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "企业用户不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # 获取所有企业下所有用户的在运的订单
    process_list = RentLeaseInfo.objects.filter(on_site__isnull=False, user_id__enterprise=user.enterprise)
    page = paginator.paginate_queryset(process_list, request)
    ret_ser = RentLeaseInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)

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
from rentservice.models import UserAppointment
from rentservice.models import NotifyMessage
import pytz
from django.conf import settings


log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


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


# 用户面板数据统计（未完成的预约单数量，在运的箱子数量，通知数量）
@csrf_exempt
@api_view(['GET'])
def get_dash_data(request, user_id):
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "运输用户不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # 获取未完成预约单数量
    appointment_count = UserAppointment.objects.filter(user_id=user, flag=0).count()
    # 获取在运箱子数量
    box_count = RentLeaseInfo.objects.filter(user_id=user, on_site__isnull=True).count()
    # 获取通知数量
    notify_count = NotifyMessage.objects.filter(user=user,read_flag='N').count()
    return JsonResponse(
        retcode({'appointment_count': appointment_count, 'box_count': box_count, 'notify_count': notify_count}, '0000',
                'Success'), safe=True, status=status.HTTP_200_OK)

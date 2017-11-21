#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rentservice.models import EnterpriseUser
from rentservice.models import NotifyMessage
from rentservice.serializers import NotifyMessageSerializer
from rentservice.utils.retcode import *
from rest_framework.parsers import JSONParser
import uuid
import datetime

import pytz
from django.conf import settings

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


# 查询消息列表
@csrf_exempt
@api_view(['GET'])
def get_notify_list_by_user(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户信息不存在"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    notify_list = NotifyMessage.objects.filter(user=user).order_by('-notify_time', 'read_flag')
    page = paginator.paginate_queryset(notify_list, request)
    ret_ser = NotifyMessageSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 修改标志
@csrf_exempt
@api_view(['POST'])
def set_notify_read_flag(request):
    data = JSONParser().parse(request)
    try:
        notify_id = data['notify_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入消息id"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        read_flag = data['read_flag']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入已读标志"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        notify = NotifyMessage.objects.get(notify_id=notify_id)
    except NotifyMessage.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "消息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    notify.read_flag = read_flag
    notify.save()
    return JsonResponse(retcode(NotifyMessageSerializer(notify).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 删除消息
@csrf_exempt
@api_view(['DELETE'])
def delete_notify(request, notify_id):
    try:
        NotifyMessage.objects.get(notify_id=notify_id).delete()
    except NotifyMessage.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "消息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode({}, "0000", "消息删除成功"), safe=True, status=status.HTTP_200_OK)


def create_notify(title, content, user_id):
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
        notify = NotifyMessage(notify_title=title, notify_content=content, user=user,
                               notify_time=datetime.datetime.now(tz=tz), read_flag='N')
        notify.save()
    except Exception as e:
        log.error(e)

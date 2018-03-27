#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from tms.models import User
from tms.models import NotifyMessage
from tms.serializers import NotifyMessageSerializer
from tms.utils.retcode import *
from rest_framework.parsers import JSONParser
import datetime

import pytz
from django.conf import settings

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


# 查询告警消息列表
@csrf_exempt
@api_view(['GET'])
def get_notify_list_by_user(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()

    alarm_list = NotifyMessage.objects.filter(user_id=user_id).order_by('-time', 'read_flag')
    page = paginator.paginate_queryset(alarm_list, request)
    ret_ser = NotifyMessageSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 修改告警消息已读标志
@csrf_exempt
@api_view(['POST'])
def set_notify_read_flag(request):
    try:
        data = json.loads(request.body)
        notify_id = data['notify_id']
        read_flag = data['read_flag']

        notify = NotifyMessage.objects.get(notify_id=notify_id)
        notify.read_flag = read_flag
        notify.save()
    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'save fishing success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)



# 删除消息
@csrf_exempt
@api_view(['DELETE'])
def delete_notify(request, notify_id):
    try:
        NotifyMessage.objects.get(notify_id=notify_id).delete()
    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'Delete message success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)



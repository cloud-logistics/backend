#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rentservice.utils.retcode import *
from django.db import transaction
from rentservice.models import UserAppointment
from rentservice.models import AppointmentDetail
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')


# 创建预约单
@csrf_exempt
@api_view(['POST'])
def create_appointment(request):
    data = JSONParser().parse(request)
    try:
        user_id = data['user_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入承运用户id"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        site_total = data['site_total']
        if len(site_total) == 0:
            raise Exception
    except Exception:
        return JsonResponse(retcode({}, "9999", "堆场预约箱子数不能为空"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        total = data['total']
        if len(total) == 0:
            raise Exception
    except Exception:
        return JsonResponse(retcode({}, "9999", "预约箱子总数不能为空"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        with transaction.atomic():
            # 获取预约码
            appointment_code = UserAppointment.objects.raw(
                '''SELECT to_char(now(),'YYYYMMDD')||lpad(nextval('iot.appointment_code')::TEXT,8,'0')''')
            print appointment_code
    except Exception as e:
        log.error(e)
    return JsonResponse(retcode({}, "0000", "Success"), safe=True, status=status.HTTP_200_OK)

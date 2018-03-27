#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Alarm of tms'''

from cloudbox import celery
from rentservice.utils.redistools import RedisTool
from tms.models import SensorData, TruckFlume, FishingHistory, FishType, NotifyMessage
from util import logger
import datetime
import pytz
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
import json

USER_ALIAS_ID_HASH = 'user_alias_id_hash'

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


def judge_alarm(sensors):
    for s in sensors:
        try:
            flumes = TruckFlume.objects.filter(deviceid=s['deviceid'])
            if len(flumes) == 0:
                continue

            flume_id = flumes[0].flume_id
            user_id = flumes[0].user.user_id

            fishing = FishingHistory.objects.filter(flume_id=flume_id, order_status=1)
            if len(fishing) == 0:
                continue

            type_id = fishing[0].fish_type.type_id
            fish_type = FishType.objects.get(type_id=type_id)
            msg = ''
            if s['temperature'] > fish_type.temperature_max:
                msg = '当前温度：' + str(s['temperature']) + '，超过最高温度阈值：' + str(fish_type.temperature_max) + ';'
            elif s['temperature'] < fish_type.temperature_min:
                msg = '当前温度：' + str(s['temperature']) + '，低于最低温度阈值：' + str(fish_type.temperature_min) + ';'

            if s['salinity'] > fish_type.salinity_max:
                msg += '当前盐度：' + str(s['salinity']) + '，超过最高盐度阈值：' + str(fish_type.salinity_max)+ ';'
            elif s['salinity'] < fish_type.salinity_min:
                msg += '当前盐度：' + str(s['salinity']) + '，低于最低盐度阈值：' + str(fish_type.salinity_min) + ';'

            if s['ph'] > fish_type.ph_max:
                msg += '当前PH值：' + str(s['ph']) + '，超过最高PH阈值：' + str(fish_type.ph_max) + ';'
            elif s['ph'] < fish_type.ph_min:
                msg += '当前PH值：' + str(s.ph) + '，低于最低PH阈值：' + str(fish_type.ph_min)+ ';'

            if s['dissolved_oxygen'] > fish_type.dissolved_oxygen_max:
                msg += '当前水溶氧：' + str(s['dissolved_oxygen']) + '，超过最高水溶氧阈值：' + str(fish_type.dissolved_oxygen_max) + ';'
            elif s['dissolved_oxygen'] < fish_type.dissolved_oxygen_min:
                msg += '当前水溶氧：' + str(s['dissolved_oxygen']) + '，低于最低水溶氧阈值：' + str(fish_type.dissolved_oxygen_min) + ';'

            notify_alarm(msg, user_id)
            save_alarm(msg, user_id, s['deviceid'], fishing[0].qr_id)

        except Exception, e:
            log.error(repr(e))


def notify_alarm(message, user_id):
    conn = get_connection_from_pool()
    if conn.hexists(USER_ALIAS_ID_HASH, user_id):
        alias = []
        alias.append(conn.hget(USER_ALIAS_ID_HASH, user_id))
        celery.send_push_message.delay(alias, message)
        log.debug(message)


def save_alarm(content, user_id, deviceid, qr_id):
    try:
        alarm = NotifyMessage(title='云箱告警', content=content, user_id=user_id, deviceid=deviceid,
                               qr_id=qr_id, time=datetime.datetime.now(tz=tz), read_flag='N')
        alarm.save()
    except Exception as e:
        log.error(e)


def get_connection_from_pool():
    redis_pool = RedisTool()
    return redis_pool.get_connection()


@csrf_exempt
@api_view(['POST'])
def create_alarm(request):
    sensors = json.loads(request.body)
    judge_alarm(sensors)
    response_msg = {'status': 'OK', 'msg': 'create alarm success.'}
    return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

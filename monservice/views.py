#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from util.db import save_to_db, query_list
from util import logger

# Create your views here.

log = logger.get_logger('monservice.view.py')
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'mock_data.json'


@csrf_exempt
def containers_overview(request):
    try:
        with open(str(file_path)) as f:
            load_dict = json.load(f)
        return JsonResponse(load_dict, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('containers_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False ,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def satellites_overview(request):
    try:
        with open(str(file_path)) as f:
            load_dict = json.load(f)
        return JsonResponse(load_dict, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('satellites_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def realtime_message(request):
    pass


@csrf_exempt
def realtime_position(request):
    pass


@csrf_exempt
def history_path(request):
    pass


@csrf_exempt
def alarm_monitor(request):
    pass


@csrf_exempt
def basic_info(request):
    data = query_list('select clientid, type, produce_area, manufacturer, carrier, date_of_production ' \
                      'from iot.box_info')
    ret_list = []
    for item in data:
        dicitem = {}
        dicitem['containerId'] = to_str(item[0])
        dicitem['containerType'] = to_str(item[1])
        dicitem['factoryLocation'] = to_str(item[2])
        dicitem['factory'] = to_str(item[3])
        dicitem['carrier'] = to_str(item[4])
        dicitem['factoryDate'] = to_str(item[5])
        ret_list.append(dicitem)

    ret_dic = {'basicInfo': ret_list}

    return JsonResponse(ret_dic, safe=False, status=status.HTTP_200_OK)


@csrf_exempt
def history_message(request):
    pass


@csrf_exempt
def status_summary(request):
    pass


def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value

#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Flow of tms'''


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from tms.models import FishingHistory, Fishery, Unit, FishType, OperateHistory
import json
import uuid
import datetime
from util import logger
import time

log = logger.get_logger('monservice.site.py')


# 获取二维码ID
@csrf_exempt
@api_view(['GET'])
def get_order(request):
    try:
       order_id = str(uuid.uuid1())

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        link = 'http://goodsrider.hnaresearch.com/order?qr_id='
        response_msg = {'status':'OK', 'msg': 'get order id success.', 'qr_id': order_id, 'link': link + order_id}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 捕捞
@csrf_exempt
@api_view(['POST'])
def fishing(request):
    try:
        user_id = request.GET.get('user_id')

        data = json.loads(request.body)
        QR_id = data['qr_id']
        fish_type = data['fish_type_id']
        fishery = data['fishery_id']
        weight = data['weight']
        unit = data['unit_id']

        # 订单
        order = FishingHistory(QR_id=QR_id, fish_type_id=fish_type, fishery_id=fishery,  weight=weight, unit_id=unit)
        order.save()

        # 流水
        ts = str(time.time())[0:10]
        op = OperateHistory(QR_id=QR_id, timestamp=ts, operate_type=1, user_id=user_id)
        op.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'save fishing success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 装车
@csrf_exempt
@api_view(['POST'])
def load_up(request):
    try:
        user_id = request.GET.get('user_id')

        data = json.loads(request.body)
        qr_id = data['qr_id']

        order = FishingHistory.objects.get(qr_id=qr_id)
        flume_id = data['flume_id']
        order.flume = flume_id
        order.save()

        # 流水
        ts = str(time.time())[0:10]
        op = OperateHistory(qr_id=qr_id, timestamp=ts, operate_type=2, user=user_id)
        op.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'load up success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 卸载
@csrf_exempt
@api_view(['POST'])
def load_off(request, user_id):
    try:
        data = json.loads(request.body)
        qr_id = data['qr_id']

        # 结束
        order = FishingHistory.objects.get(qr_id=qr_id)
        order.status = 0
        order.save()

        # 流水
        ts = str(time.time())[0:10]
        op = OperateHistory(qr_id=qr_id, timestamp=ts, operate_type=3, user=user_id)
        op.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'load off success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_fishery_list(request):
    try:
        fishery_list = Fishery.objects.all()
        res_fishery = []
        for item in fishery_list:
            res_fishery.append(
                {'fishery_id': item.fishery_id, 'fishery_name': item.fishery_name, 'longitude': item.longitude, 'latitude': item.latitude})

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'get fishery list success.', 'data': res_fishery}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_fishtype_list(request):
    try:
        fishtype_list = FishType.objects.all()
        res_fishtype = []
        for item in fishtype_list:
            res_fishtype.append({'type_id': item.type_id, 'type_name': item.type_name})

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get fish type list success.', 'data': res_fishtype}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_unit_list(request):
    try:
        unit_list = Unit.objects.all()
        res_unit_list = []

        for item in unit_list:
            res_unit_list.append({'unit_id': item.unit_id, 'unit_name': item.unit_name})

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get unit list success.', 'data': res_unit_list}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)
#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Flow of tms'''


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from tms.models import FishingHistory, Fishery, Unit, FishType, OperateHistory, TruckFlume
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


def get_operation_by_type(op_type):
    if op_type == 0:
        op = '捕捞'
    elif op_type == 1:
        op = '装车'
    elif op_type == 2:
        op = '收货'
    else:
        op = '错误操作类型'
    return op


def get_operation_res_msg(s):
    op_msg = get_operation_by_type(s)
    err_msg = '该订单已' + op_msg + '，不能重复操作！'
    response_msg = {'status': 'ERROR', 'msg': err_msg}
    return response_msg


# 捕捞
@csrf_exempt
@api_view(['POST'])
def fishing(request):
    try:

        data = json.loads(request.body)
        qr_id = data['qr_id']
        o = FishingHistory.objects.filter(qr_id=qr_id)
        if len(o) > 0:
            s = o[0].order_status
            response_msg = get_operation_res_msg(s)
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        user_id = data['user_id']
        fish_type = data['fish_type_id']
        fishery = data['fishery_id']
        weight = data['weight']
        unit = data['unit_id']

        # 订单
        order = FishingHistory(qr_id=qr_id, fish_type_id=fish_type, fishery_id=fishery,  weight=weight, unit_id=unit)
        order.save()

        # 流水
        ts = str(time.time())[0:10]
        op = OperateHistory(qr_id=qr_id, timestamp=ts, op_type=1, user_id=user_id)
        op.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'save fishing success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 装车
@csrf_exempt
@api_view(['POST'])
def load_up(request):
    try:
        data = json.loads(request.body)

        user_id = data['user_id']
        qr_id = data['qr_id']
        order = FishingHistory.objects.get(qr_id=qr_id)
        s = order.order_status
        if s >= 1:
            response_msg = get_operation_res_msg(s)
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        flume_id = data['flume_id']
        order.flume_id = flume_id
        order.order_status = 1
        order.save()

        # 流水
        ts = str(time.time())[0:10]
        op = OperateHistory(qr_id=qr_id, timestamp=ts, op_type=2, user_id=user_id)
        op.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'load up success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 卸载
@csrf_exempt
@api_view(['POST'])
def load_off(request):
    try:
        data = json.loads(request.body)

        user_id = data['user_id']
        qr_id = data['qr_id']

        # 结束
        order = FishingHistory.objects.get(qr_id=qr_id)
        s = order.order_status
        if s >= 2:
            response_msg = get_operation_res_msg(s)
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        order.order_status = 2
        order.save()

        # 流水
        ts = str(time.time())[0:10]
        op = OperateHistory(qr_id=qr_id, timestamp=ts, op_type=3, user_id=user_id)
        op.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
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
        response_msg = {'status': 'ERROR', 'msg': e.message}
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
        response_msg = {'status': 'ERROR', 'msg': e.message}
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
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get unit list success.', 'data': res_unit_list}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_flume_list(request):
    try:
        user_id = request.GET.get('user_id')
        flume_list = TruckFlume.objects.filter(user_id=user_id)

        res_flume_list = []
        for item in flume_list:
            res_flume_list.append({'flume_id': item.flume_id})

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get flume list success.', 'data': res_flume_list}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_fishing_detail(request, qr_id):
    try:
        fishing = FishingHistory.objects.get(qr_id=qr_id)
        fishery = Fishery.objects.get(fishery_id=fishing.fishery_id)
        fish_type = FishType.objects.get(type_id=fishing.fish_type_id)
        unit = Unit.objects.get(unit_id=fishing.unit_id)

        res_fishing = {}

        fishing_op = OperateHistory.objects.filter(qr_id=qr_id, op_type=1).order_by('timestamp')
        if len(fishing_op) > 0:
            res_fishing['fishing_timestamp'] = fishing_op[0].timestamp * 1000
            res_fishing['fishing_man_id'] = fishing_op[0].user.user_id
            res_fishing['fishing_man'] = fishing_op[0].user.user_name
        else:
            res_fishing['fishing_timestamp'] = 0

        load_up = OperateHistory.objects.filter(qr_id=qr_id, op_type=2).order_by('timestamp')
        if len(load_up) > 0:
            res_fishing['load_timestamp'] = load_up[0].timestamp * 1000
        else:
            res_fishing['load_timestamp'] = 0

        delivery = OperateHistory.objects.filter(qr_id=qr_id, op_type=2).order_by('timestamp')
        if len(delivery) > 0:
            res_fishing['delivery_timestamp'] = delivery[0].timestamp * 1000
        else:
            res_fishing['delivery_timestamp'] = 0

        res_fishing['fishery_id'] = fishery.fishery_id
        res_fishing['fishery_name'] = fishery.fishery_name
        res_fishing['fish_type_id'] = fish_type.type_id
        res_fishing['fish_type_name'] = fish_type.type_name
        res_fishing['weight'] = fishing.weight
        res_fishing['unit_id'] = unit.unit_id
        res_fishing['unit_name'] = unit.unit_name


    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'get fishing detail success.', 'data': res_fishing}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)
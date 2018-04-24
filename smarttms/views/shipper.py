#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from django.db.models import Max, Min
import json
from util import logger
from smarttms.models import ShopInfo, GoodsList, SensorData, BoxInfo, GoodsOrder, GoodsOrderDetail, OrderItem
from rest_framework.settings import api_settings
import uuid
import datetime


log = logger.get_logger(__name__)


# 查询云箱列表
@csrf_exempt
@api_view(['GET'])
def get_box_list(request):
    try:
        if 'user_id' in request.GET:
            user_id = request.GET.get('user_id')
        all_boxes = GoodsOrderDetail.objects.filter(order__user__user_id=user_id)

        resp_using_boxes = []
        resp_transporting_boxes = []
        resp_unused_boxes = []
        for item in all_boxes:
            temperature_threshold_min = item.box.type.temperature_threshold_min
            temperature_threshold_max = item.box.type.temperature_threshold_max
            box_sensor_data = SensorData.objects.filter(deviceid=item.box.deviceid).order_by('-timestamp')
            if len(box_sensor_data) > 0:
                latest_data = box_sensor_data[0]
            status = '正常'
            if latest_data.temperature < temperature_threshold_min:
                status = '温度过低'
            elif latest_data.temperature > temperature_threshold_max:
                status = '温度过高'

            box_item =  {"deviceid": item.box.deviceid, "latitude": latest_data.latitude, "longitude": latest_data.longitude,
                         "type_name": item.box.type.type_name, "status": status}

            if item.order.state == 0:
                resp_unused_boxes.append(box_item)

            elif item.order.state == 1:
                resp_transporting_boxes.append(box_item)

            elif item.order.state == 2:
                resp_using_boxes.append(box_item)

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get box list success.', 'using': resp_using_boxes, 'transporting': resp_transporting_boxes, 'unused': resp_unused_boxes}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 查询门店列表
@csrf_exempt
@api_view(['GET'])
def get_shop_list(request):
    try:
        shop_list = ShopInfo.objects.all()
        res_shops = []
        for item in shop_list:
            res_shops.append(
                {'shop_id': item.id, 'shop_name': item.name, 'shop_location': item.location})
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get shop list success.', 'data': res_shops}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 查询货物列表
@csrf_exempt
@api_view(['GET'])
def get_goods_list(request):
    try:
        goods_list = GoodsList.objects.all()
        res_goods = []
        for item in goods_list:
            res_goods.append(
                {'goods_id': item.id, 'goods_name': item.type.name, 'ava_number': item.num, 'goods_unit': item.unit.name}
            )

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get goods list success.', 'data': res_goods}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 查询云箱详情
@csrf_exempt
@api_view(['GET'])
def get_box_detail(request):
    try:
        if 'user_id' in request.GET:
            user_id = request.GET.get('user_id')
        if 'deviceid' in request.GET:
            deviceid = request.GET.get('deviceid')

        order_details = GoodsOrderDetail.objects.filter(deviceid=deviceid, order__user__user_id=user_id)
        if len(order_details) > 0:
            detail = order_details[0]
            deviceid = detail.box.deviceid

            box_sensor_data = SensorData.objects.filter(deviceid=deviceid).order_by('-timestamp')
            if len(box_sensor_data) > 0:
                latest_data = box_sensor_data[0]
            temperature_threshold_min = detail.box.type.temperature_threshold_min
            temperature_threshold_max = detail.box.type.temperature_threshold_max
            status = '正常'
            if latest_data.temperature < temperature_threshold_min:
                status = '温度过低'
            elif latest_data.temperature > temperature_threshold_max:
                status = '温度过高'

            use_time = (datetime.datetime.now() - detail.order.order_start_time).seconds
            box_detail = {'deviceid': deviceid, 'latitude': latest_data.latitude, 'longitude': latest_data.longitude,
                          'use_time': use_time, 'status': status, 'shop_tel': detail.order.shop.telephone}

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get box detail success.', 'data': box_detail}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 创建运单
@csrf_exempt
@api_view(['POST'])
def create_goodsorder(request):
    try:
        data = json.loads(request.body)
        shop_id = data['shop_id']
        user_id = data['user_id']
        site_id = data['site_id']

        goods_order_id = str(uuid.uuid1())
        go = GoodsOrder(id=goods_order_id, order_start_time=datetime.datetime.now(), state=0, site_id=site_id, shop_id=shop_id, user_user_id=user_id)
        go.save()

        box_list = data['boxes']
        for box in box_list:
            deviceid = box['deviceid']
            detail_id = str(uuid.uuid1())

            gd = GoodsOrderDetail(order_detail_id=detail_id, order=go, box_deviceid=deviceid)
            gd.save()

            goods_list = box['goods']
            for goods in goods_list:
                goods_id = goods['goods_id']
                goods_num = goods['goods_num']
                item_id = str(uuid.uuid1())
                item = OrderItem(id=item_id, goods_id=goods_id, goods_unit=goods.unit, num=goods_num, order_detail=gd)
                item.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'Add goods order success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

# 获取运单列表
@csrf_exempt
@api_view(['GET'])
def get_order_list(request):
    try:
        if 'user_id' in request.GET:
            user_id = request.GET.get('user_id')

        goods_orders = GoodsOrder.objects.filter(user__user_id=user_id)
        resp_orders = []
        for go in goods_orders:
            item_list = OrderItem.objects.filter(order_detail__order=go)
            goods_items = []
            for item in item_list:
                goods_items.append({'goods_id': item.goods.id, 'goods_name': item.goods.name,
                                    'goods_unit': item.unit.name, 'number': item.num})

            status = '正常'
            resp_orders.append({'order_id': go.id, 'order_time': go.order_start_time, 'shop_id': go.shop.id,
                                'shop_name': go.shop.name, 'status': status, 'goods': resp_orders})
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get order list success.', 'data': resp_orders}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 修改运单
@csrf_exempt
@api_view(['PUT'])
def update_goods_order(request, order_id):
    try:
        data = json.loads(request.body)
        shop_id = data['shop_id']
        site_id = data['site_id']

        go = GoodsOrder.objects.get(id=order_id)
        go.shop.id = shop_id
        go.site.id = site_id
        go.save()

        GoodsOrderDetail.objects.filter(order_id=order_id).delete()

        box_list = data['boxes']
        for box in box_list:
            deviceid = box['deviceid']
            detail_id = str(uuid.uuid1())
            gd = GoodsOrderDetail(order_detail_id=detail_id, order=go, box_deviceid=deviceid)
            gd.save()

            goods_list = box['goods']
            for goods in goods_list:
                goods_id = goods['goods_id']
                goods_num = goods['goods_num']
                item_id = str(uuid.uuid1())
                item = OrderItem(id=item_id, goods_id=goods_id, goods_unit=goods.unit, num=goods_num, order_detail=gd)
                item.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'Update goods order success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 删除运单
@csrf_exempt
@api_view(['DELETE'])
def delete_goods_order(request, order_id):
    try:
        GoodsOrder.objects.get(id=order_id).delete()
    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'Delete goods order success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


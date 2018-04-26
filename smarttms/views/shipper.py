#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import status
import json
from util import logger
from smarttms.models import ShopInfo, GoodsList, SensorData, BoxInfo, GoodsOrder, GoodsOrderDetail, OrderItem
from rest_framework.settings import api_settings
import uuid
import datetime
from util.geo import cal_position


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
            box_status = '正常'
            if float(latest_data.temperature) < temperature_threshold_min:
                box_status = '温度过低'
            elif float(latest_data.temperature) > temperature_threshold_max:
                box_status = '温度过高'

            box_item =  {"deviceid": item.box.deviceid, "latitude": str(cal_position(latest_data.latitude)), "longitude": str(cal_position(latest_data.longitude)),
                         "type_name": item.box.type.box_type_name, "status": box_status}

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
                {'goods_id': item.id, 'goods_name': item.name, 'ava_number': item.num, 'goods_unit': item.unit.name}
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

        box_status = u'正常'
        order_details = GoodsOrderDetail.objects.filter(box__deviceid=deviceid, order__user__user_id=user_id)
        if len(order_details) > 0:
            detail = order_details[0]
            deviceid = detail.box.deviceid

            box_sensor_data = SensorData.objects.filter(deviceid=deviceid).order_by('-timestamp')
            if len(box_sensor_data) > 0:
                latest_data = box_sensor_data[0]
            temperature_threshold_min = detail.box.type.temperature_threshold_min
            temperature_threshold_max = detail.box.type.temperature_threshold_max
            if float(latest_data.temperature) < temperature_threshold_min:
                box_status = u'温度过低'
            elif float(latest_data.temperature) > temperature_threshold_max:
                box_status = u'温度过高'

            use_time = (datetime.datetime.now() - detail.order.order_start_time.replace(tzinfo=None)).seconds
            box_detail = {'deviceid': deviceid, "latitude": str(cal_position(latest_data.latitude)), "longitude": str(cal_position(latest_data.longitude)),
                          'use_time': use_time, 'status': box_status, 'shop_tel': detail.order.shop.telephone}

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
        go = GoodsOrder(id=goods_order_id, order_start_time=datetime.datetime.now(), state=0, site_id=site_id, shop_id=shop_id, user_id=user_id)
        go.save()

        box_list = data['boxes']
        for box in box_list:
            deviceid = box['deviceid']
            detail_id = str(uuid.uuid1())
            boxinfo = BoxInfo.objects.get(deviceid=deviceid)

            gd = GoodsOrderDetail(id=detail_id, order=go, box=boxinfo)
            gd.save()

            goods_list = box['goods']
            for goods in goods_list:
                goods_id = goods['goods_id']
                goods_num = goods['goods_num']
                item_id = str(uuid.uuid1())
                gs = GoodsList.objects.get(id=goods_id)
                item = OrderItem(id=item_id, goods_id=goods_id, goods_unit=gs.unit, num=goods_num, order_detail=gd)
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
                                    'goods_unit': item.goods_unit.name, 'number': item.num})

            box_status = '正常'
            resp_orders.append({'order_id': go.id, 'order_time': go.order_start_time, 'shop_id': go.shop.id,
                                'shop_name': go.shop.name, 'status': box_status, 'goods': goods_items})
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get order list success.', 'data': resp_orders}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)



# 获取运单列表
@csrf_exempt
@api_view(['GET'])
def get_transporting_goods_orders(request):
    try:
        if 'user_id' in request.GET:
            user_id = request.GET.get('user_id')

        goods_orders = GoodsOrder.objects.filter(user__user_id=user_id, driver_take_status=1, receiver_take_status=0)
        resp_orders = []
        for go in goods_orders:
            item_list = OrderItem.objects.filter(order_detail__order=go)
            goods_items = []
            for item in item_list:
                goods_items.append({'goods_id': item.goods.id, 'goods_name': item.goods.name,
                                    'goods_unit': item.goods_unit.name, 'number': item.num})

            box_status = '正常'
            resp_orders.append({'order_id': go.id, 'order_time': go.order_start_time, 'shop_id': go.shop.id,
                                'shop_name': go.shop.name, 'status': box_status, 'driver_name': go.driver.user_name,
                                'driver_tel': go.driver.user_phone, 'goods': goods_items})
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get transporting order list success.', 'data': resp_orders}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)



# 获取运单列表
@csrf_exempt
@api_view(['GET'])
def get_orders_by_day(request):
    try:
        if 'user_id' in request.GET:
            user_id = request.GET.get('user_id')

        if 'begin_time' in request.GET and 'end_time' in request.GET:
            begin_timestamp = request.GET.get('begin_time')
            end_timestamp = request.GET.get('end_time')
            begin_time = datetime.datetime.fromtimestamp(begin_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.fromtimestamp(end_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        goods_orders = GoodsOrder.objects.filter(user__user_id=user_id, order_start_time__gte=begin_time, order_start_time__lte=end_time)
        resp_orders = []
        for go in goods_orders:
            item_list = OrderItem.objects.filter(order_detail__order=go)
            goods_items = []
            for item in item_list:
                goods_items.append({'goods_id': item.goods.id, 'goods_name': item.goods.name,
                                    'goods_unit': item.goods_unit.name, 'number': item.num})
            box_status = '正常'
            resp_orders.append({'order_id': go.id, 'order_time': go.order_start_time, 'shop_id': go.shop.id,
                                'shop_name': go.shop.name, 'status': box_status, 'driver_name': go.driver.user_name,
                                'driver_tel': go.driver.user_phone, 'goods': goods_items})
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get transporting order list success.', 'data': resp_orders}
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 获取运单详情
@csrf_exempt
@api_view(['GET'])
def get_goods_order(request, order_id):
    try:
        goods_order = GoodsOrder.objects.get(id=order_id)
        box_list = []
        gds = GoodsOrderDetail.objects.filter(order=goods_order)
        for detail in gds:

            goods_items = []
            items = OrderItem.objects.filter(order_detail=detail)
            for item in items:
                goods_items.append({'goods_id': item.id, 'goods_name': item.goods.name, 'goods_num': item.num})

            sds = SensorData.objects.filter(deviceid=detail.box.deviceid).order_by('-timestamp')
            if len(sds) > 0:
                box_sensor = sds[0]
                box = {'deviceid': detail.box.deviceid, 'box_type': detail.box.type.box_type_name,
                       'temperature': box_sensor.temperature, 'goods': goods_items}

            box_list.append(box)

        resp_order = {'order_id': goods_order.id, 'order_time': goods_order.order_start_time, 'shop_id': goods_order.shop.id,
                      'shop_name': goods_order.shop.name, 'shop_tel': goods_order.shop.telephone, 'status': u'正常',
                      'driver_name': goods_order.driver.user_name, 'driver_tel': goods_order.driver.user_phone, 'boxes': box_list}

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        resp = {'status': 'OK', 'msg': 'Get transporting order list success.', 'data': resp_order}
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
            boxinfo = BoxInfo.objects.get(deviceid=deviceid)
            gd = GoodsOrderDetail(id=detail_id, order=go, box=boxinfo)
            gd.save()

            goods_list = box['goods']
            for goods in goods_list:
                goods_id = goods['goods_id']
                goods_num = goods['goods_num']
                item_id = str(uuid.uuid1())
                gs = GoodsList.objects.get(id=goods_id)
                item = OrderItem(id=item_id, goods_id=goods_id, goods_unit=gs.unit, num=goods_num, order_detail=gd)
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


def get_box_status(box):
    try:
        box_sensor_data = SensorData.objects.filter(deviceid=box.deviceid).order_by('-timestamp')
        if len(box_sensor_data) > 0:
            latest_data = box_sensor_data[0]
        temperature_threshold_min = box.type.temperature_threshold_min
        temperature_threshold_max = box.type.temperature_threshold_max
        box_status = u'正常'
        if float(latest_data.temperature) < temperature_threshold_min:
            box_status = u'温度过低'
        elif float(latest_data.temperature) > temperature_threshold_max:
            box_status = u'温度过高'
        return box_status
    except Exception, e:
        log.error(e.message)


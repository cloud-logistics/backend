#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse
from util import logger
from smarttms.utils.retcode import retcode, errcode
from smarttms.utils.logger import get_logger
from smarttms.models import GoodsOrderDetail, GoodsOrder
from smarttms.serializers import GoodsOrderSerializer


log = get_logger(__name__)


@csrf_exempt
@api_view(['GET'])
def order_info(request, deviceid):
    try:
        goods_order_detail = GoodsOrderDetail.objects.get(box__deviceid=deviceid, driver_take_status=0)
    except GoodsOrderDetail.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0400", '云箱不存在'), "0400", '云箱不存在'), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    ser_goods_order = GoodsOrderSerializer(goods_order_detail.order)
    ret = ser_goods_order.data
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def ack_order(request):
    ret = {}
    data = JSONParser().parse(request)
    try:
        deviceid = data['deviceid']
    except Exception:
        return JsonResponse(retcode({}, "9999", '云箱id不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        goods_order_detail = GoodsOrderDetail.objects.get(box__deviceid=deviceid, driver_take_status=0)
    except GoodsOrderDetail.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0400", '云箱不存在'), "0400", '云箱不存在'), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        goods_order_detail.driver_take_status = 1
        goods_order_detail.save()
        goods_order_detail_list = GoodsOrderDetail.objects.filter(order=goods_order_detail.order)
        detail_total_num = goods_order_detail_list.count()
        detail_ack_num = 0
        for item in goods_order_detail_list:
            if item.driver_take_status == 1:
                detail_ack_num = + 1
            else:
                continue
        if detail_ack_num == detail_total_num and detail_ack_num != 0:
            goods_order = goods_order_detail.order
            goods_order.driver_take_status = 1
            ret['shop_id'] = goods_order.shop.id
            goods_order.save()
            log.info("the goods order has been ack")
    except Exception, e:
        log.error(repr(e))
    ret['detail_total_num'] = detail_total_num
    ret['detail_ack_num'] = detail_ack_num
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
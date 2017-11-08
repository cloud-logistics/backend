#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.serializers import SiteFullInfoSerializer, BoxFullInfoSerializer
import json
from monservice.models import SiteInfo, City, Province, Nation, BoxTypeInfo, BoxInfo, SiteBoxStock, SiteDispatch
from util import logger
from rest_framework.settings import api_settings
from monservice.models import SiteHistory
import time
import datetime
from django.db import transaction

log = logger.get_logger('monservice.site.py')

# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


# 新增堆场
@csrf_exempt
@api_view(['POST'])
def add_site(request):
    try:
        data = json.loads(request.body)
        location = to_str(data['location'])             # 堆场名称

        if location == '':
            response_msg = {'status': 'ERROR', 'msg': 'location is empty.'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        longtitude = to_str(data['longitude'])          # 经度
        if longtitude == '':
            response_msg = {'status': 'ERROR', 'msg': 'longtitude is empty.'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)
        latitude = to_str(data['latitude'])             # 纬度

        if latitude == '':
            response_msg = {'status': 'ERROR', 'msg': 'latitude is empty.'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        site_code = to_str(data['site_code'])           # 堆场代码
        volume = data['volume']                         # 堆场箱子容量
        city_id = data['city_id']                       # 城市
        province_id = data['province_id']               # 省
        nation_id = data['nation_id']                   # 国家

        city = City.objects.get(id=city_id)
        province = Province.objects.get(province_id=province_id)
        nation = Nation.objects.get(nation_id=nation_id)
        site = SiteInfo(location=location, latitude=latitude, longitude=longtitude, site_code=site_code,
                        city= city, province=province, nation=nation, volume=volume)
        site.save()

        initialize_box_num(site.id)

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'add site success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)

# 删除堆场
@csrf_exempt
@api_view(['DELETE'])
def delete_site(request, id):
    try:
        SiteInfo.objects.get(id=id).delete()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'delete site success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 修改堆场
@csrf_exempt
@api_view(['PUT'])
def modify_site(request, id):
    try:
        data = json.loads(request.body)

        site = SiteInfo.objects.get(id=id)
        site.location = to_str(data['location'])  # 堆场名称
        site.longitude = to_str(data['longitude'])  # 经度
        site.latitude = to_str(data['latitude'])  # 纬度
        site.site_code = to_str(data['site_code'])  # 堆场代码
        site.volume = data['volume']  # 堆场箱子容量

        city_id = data['city_id']  # 城市
        province_id = data['province_id']  # 省
        nation_id = data['nation_id']  # 国家
        city = City.objects.get(id=city_id)
        province = Province.objects.get(province_id=province_id)
        nation = Nation.objects.get(nation_id=nation_id)
        site.city = city
        site.province = province
        site.nation = nation
        site.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'modify site success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 获取全部堆场信息
@csrf_exempt
@api_view(['GET'])
def get_sites(request):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        sites = SiteInfo.objects.all().order_by('id')
        page = paginator.paginate_queryset(sites, request)
        ret_ser = SiteFullInfoSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query sites success')


# 根据堆场ID获取堆场内的云箱
@csrf_exempt
@api_view(['GET'])
def get_site_boxes(request, id):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        boxes = BoxInfo.objects.filter(siteinfo_id=id).order_by('deviceid')
        page = paginator.paginate_queryset(boxes, request)
        ret_ser = BoxFullInfoSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query sites box success')


# 仓库箱子热力图
@csrf_exempt
@api_view(['GET'])
def get_box_by_allsite(request):

    try:
        site_list = SiteInfo.objects.all().order_by('id')
        res_site = []
        for item in site_list:
            stocks = SiteBoxStock.objects.filter(site=item)
            site_box_num = 0
            for stock in stocks:
                site_box_num += stock.ava_num

            res_site.append(
                {'id': item.id, 'location': item.location, 'latitude': item.latitude, 'longitude': item.longitude,
                 'site_code': item.site_code, 'box_num': site_box_num})

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        response_msg = {'sites': res_site, 'status': 'OK', 'msg': 'query distribution success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 获取某个堆场箱子进出流水
@csrf_exempt
@api_view(['GET'])
def get_site_stream(request, id):
    try:
        ret_data = []
        data = SiteHistory.objects.filter(site_id=id)
        for record in data:
            ts = record.timestamp
            box_id = record.box_id
            type = record.op_type
            timestr = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            # 操作类型：1表示入仓，0表示出仓
            if type == 1:
                typestr = '入库'
            else:
                typestr = '出库'

            ret_data.append({'timestamp': timestr, 'box_id': box_id, 'type': typestr})
        resp = {'site_id': str(id), 'siteHistory': ret_data}
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 箱子入库、出库接口
@csrf_exempt
@api_view(['POST'])
def box_inout(request):
    try:
        data = json.loads(request.body)
        site_id = str(data['site_id'])  # 堆场id
        boxes = data['boxes']  # 箱子数组
        ts = str(time.time())[0:10]
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])  # 箱子id
                type = str(box['type'])  # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site_id=site_id, box_id=box_id, op_type=type)
                history.save()

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                stock = SiteBoxStock.objects.get(site_id=site_id, box_type=box.type)
                if type == '1':
                    stock.ava_num += 1
                else:
                    stock.ava_num -= 1
                stock.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'post box inout success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 箱子进出仓库
def enter_leave_site(data):
    try:
        site_id = str(data['site_id'])  # 堆场id
        boxes = data['boxes']  # 箱子数组
        ts = str(time.time())[0:10]
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])  # 箱子id
                type = str(box['type'])  # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site_id=site_id, box_deviceid=box_id, op_type=type)
                history.save()

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                stock = SiteBoxStock.objects.get(site_id=site_id, box_type=box.type)
                if type == '1':
                    stock.ava_num += 1
                else:
                    stock.ava_num -= 1
                stock.save()
    except Exception, e:
        log.error(e.message)


# 创建仓库时，初始化箱子可用数
def initialize_box_num(site_id):
    try:
        types = BoxTypeInfo.objects.all()
        with transaction.atomic():
            for t in types:
                stock = SiteBoxStock(site_id=site_id, box_type=t)
                stock.save()
    except Exception, e:
        log.error(e.message)



# 调度出仓接口
@csrf_exempt
@api_view(['POST'])
def dispatchout(request):
    try:
        data = json.loads(request.body)
        dispatch_id = str(data['dispatch_id'])  # 调度id
        dispatch = SiteDispatch.objects.get(did=dispatch_id)
        dispatch.status = 'dispatching'
        site = dispatch.start
        dispatch.save()

        boxes = data['boxes']                   # 箱子数组
        ts = str(time.time())[0:10]
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])     # 箱子id
                type = '0'                      # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site=site, box_deviceid=box_id, op_type=type)
                history.save()

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                stock = SiteBoxStock.objects.get(site=site, box_type=box.type)
                stock.ava_num -= 1
                stock.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'post box inout success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)



# 调度入仓接口
@csrf_exempt
@api_view(['POST'])
def dispatchin(request):
    try:
        data = json.loads(request.body)
        dispatch_id = str(data['dispatch_id'])  # 调度id
        dispatch = SiteDispatch.objects.get(did=dispatch_id)
        site = dispatch.start
        dispatch.status = 'dispatched'
        dispatch.save()

        boxes = data['boxes']                   # 箱子数组
        ts = str(time.time())[0:10]
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])     # 箱子id
                type = '0'                      # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site=site, box_deviceid=box_id, op_type=type)
                history.save()

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                stock = SiteBoxStock.objects.get(site=site, box_type=box.type)
                stock.ava_num -= 1
                stock.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'post box inout success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)











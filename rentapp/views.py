#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from util.db import query_list, save_to_db, query_list_inject, delete_from_db
from util import logger
from monservice.models import SiteHistory
from rest_framework.decorators import api_view
import json
import time
import datetime


log = logger.get_logger(__name__)

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
        response_msg = 'OK'
        data = json.loads(request.body)
        location = to_str(data['location'])             # 堆场名称
        longtitude = to_str(data['longitude'])          # 经度
        latitude = to_str(data['latitude'])             # 纬度
        site_code = to_str(data['site_code'])           # 堆场代码
        capacity = to_str(data['capacity'])             # 堆场箱子容量

        sql = '''insert into iot.site_info(location, longitude, latitude, site_code, capacity)
                 VALUES ('%s', '%s', '%s', '%s', %s)''' % (location, longtitude, latitude, site_code, capacity)
        save_to_db(sql)

    except Exception, e:
        log.error(e.message)
        response_msg = e.message
        return JsonResponse(response_msg, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(response_msg, safe=False, status=status.HTTP_200_OK)


# 删除堆场
@api_view(['DELETE'])
def delete_site(request, id):
    try:
        response_msg = 'OK'
        sql = '''delete from iot.site_info where id = %s ''' % str(id)
        delete_from_db(sql)

    except Exception, e:
        log.error(e.message)
        response_msg = e.message
        return JsonResponse(response_msg, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(response_msg, safe=False, status=status.HTTP_200_OK)


# 修改堆场
@csrf_exempt
@api_view(['PUT'])
def modify_site(request, id):
    try:
        response_msg = 'OK'
        data = json.loads(request.body)
        site_id = str(id)        # 堆场id
        location = to_str(data['location'])  # 堆场名称
        longtitude = to_str(data['longitude'])  # 经度
        latitude = to_str(data['latitude'])  # 纬度
        site_code = to_str(data['site_code'])  # 堆场代码
        capacity = to_str(data['capacity'])  # 堆场箱子容量

        sql = '''update iot.site_info set location = '%s', longitude = '%s', latitude = '%s', site_code = '%s', capacity = %s
              where id = %s ''' % (location, longtitude, latitude, site_code, capacity, site_id)
        log.debug(sql)
        save_to_db(sql)

    except Exception, e:
        log.error(e.message)
        response_msg = e.message
        return JsonResponse(response_msg, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(response_msg, safe=False, status=status.HTTP_200_OK)


# 获取堆场
@csrf_exempt
@api_view(['GET'])
def get_sites(request):
    try:
        sql = '''select id, location, longitude, latitude, site_code, capacity from iot.site_info'''
        data = query_list(sql)
        ret_data = []
        for record in data:
            site_id = record[0]
            location = record[1]
            longitude = record[2]
            latitude = record[3]
            site_code = record[4]
            capacity = record[5]

            ret_data.append({'site_id': site_id, 'location': location, 'longitude': longitude,
                             'latitude': latitude, 'site_code': site_code, 'capacity': str(capacity)})
    except Exception, e:
        log.error(e.message)
        response_msg = e.message
        return JsonResponse(response_msg, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'siteInfo': ret_data}, safe=True, status=status.HTTP_200_OK)


# 获取某个堆场箱子进出流水
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
    except Exception, e:
        log.error(e.message)
        response_msg = e.message
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'Response': 'OK'}, safe=True, status=status.HTTP_200_OK)
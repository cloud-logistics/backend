#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
dispatch boxes between sites
'''

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.serializers import SiteInfoSerializer, SiteDispatchSerializer, SiteTypeDispatchSerializer
import json
from monservice.models import SiteInfo, SiteDispatch, SiteBoxStock, BoxTypeInfo, SiteTypeDispatch
from util import logger
from util.geo import get_distance
import datetime
import time
from rest_framework.settings import api_settings
from util.db import query_list

log = logger.get_logger('monservice.dispatch.py')
low = 0.1
high = 0.9
ave = 0.5


@csrf_exempt
@api_view(['GET'])
def get_dispatches(request):
    try:
        dispatches = SiteDispatch.objects.filter(create_date__gte=datetime.date.today()).order_by('did')
        if len(dispatches) == 0:
            dispatches = generate_dispatches()

        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(dispatches, request)
        ret_ser = SiteDispatchSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query dispatch success')


@csrf_exempt
@api_view(['GET'])
def get_dispatches_history(request):
    try:
        dispatches = SiteDispatch.objects.all().order_by('did')
        if len(dispatches) == 0:
            dispatches = generate_dispatches()

        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(dispatches, request)
        ret_ser = SiteDispatchSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query dispatch history success')


@csrf_exempt
@api_view(['GET'])
def get_dispatch_by_site(request, site_id):
    try:
        dispatches = SiteDispatch.objects.filter(start_id=site_id, status='undispatch').order_by('did')

        if len(dispatches) == 0:
            response_msg = {'result': 'False', 'code': '999999', 'msg': 'no dispatch for this site'}
        else:
            dis = dispatches[0]
            response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success', 'dispatch_id': dis.did, 'count': dis.count}
    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def create_dispatches(request):
    try:
        data = json.loads(request.body)
        did = generate_dispath_id()
        start_id = data['start_id']
        finish_id = data['finish_id']
        count = data['count']
        dispatch = SiteDispatch(did=did, count=count, start_id=start_id, finish_id=finish_id, create_date=datetime.date.today())
        dispatch.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'query dispatches success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


class DSite:
    def __init__(self, id, long, lat, volume, avanum):
        self.id = id
        self.longitude = long
        self.latitude = lat
        self.volume = volume
        self.avanum = avanum


def generate_dispatches():
    dsites = []
    sites = SiteInfo.objects.all()
    for site in sites:
        stocks = SiteBoxStock.objects.filter(site_id=site.id)
        avanum = 0
        for stock in stocks:
            avanum = avanum + stock.ava_num
        dsite = DSite(site.id, site.longitude, site.latitude, site.volume, avanum)
        dsites.append(dsite)
    get_dispatch(dsites)
    return SiteDispatch.objects.filter(create_date__gte=datetime.date.today()).order_by('did')


def get_dispatch(sites):
    low_sites, high_sites, ave_sites = divide(sites)
    if len(low_sites) > len(high_sites):
        high_sites += ave_sites

    for low_site in low_sites:
        dis_list = []
        for high_site in high_sites:
            dis = cal_distance(low_site, high_site)
            dis_list.append(dis)

        val, idx = min((val, idx) for (idx, val) in enumerate(dis_list))
        near_high_site = high_sites[idx]

        need_count = int(low_site.volume * low * 2) - low_site.avanum
        if need_count <= 0:
            continue

        offer_count = int((near_high_site.avanum - near_high_site.volume * ave) * low * 2)
        if offer_count <= 0:
            continue

        if need_count < offer_count:
            count = need_count
        else:
            count = offer_count

        if near_high_site.avanum - count < near_high_site.volume * ave:
            high_sites.remove(near_high_site)

        low_sites.remove(low_site)

        save_dispatch(near_high_site.id, low_site.id, count)


def cal_distance(start_site, finish_site):
    return get_distance(start_site.latitude, start_site.longitude, finish_site.latitude, finish_site.longitude) / 1000


def divide(sites):
    low_sites = []
    high_sites = []
    ave_sites = []
    for site in sites:
        if site.avanum < site.volume * low:
            low_sites.append(site)
        elif site.avanum > site.volume * high:
            high_sites.append(site)
        else:
            ave_sites.append(site)
    return low_sites, high_sites, ave_sites


def save_dispatch(start_id, finish_id, count):
    try:
        start_site = SiteInfo.objects.get(id=start_id)
        finish_site = SiteInfo.objects.get(id=finish_id)
        did = generate_dispath_id()

        dispatch = SiteDispatch(did=did, start=start_site, finish=finish_site, count=count, create_date=datetime.datetime.today())
        dispatch.save()
    except Exception, e:
        log.error(e.message)


@csrf_exempt
@api_view(['GET'])
def get_type_dispatches(request):
    try:
        dispatches = SiteTypeDispatch.objects.filter(create_date__gte=datetime.date.today()).order_by('did')
        if len(dispatches) == 0:
            dispatches = generate_dis_type()

        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(dispatches, request)
        ret_ser = SiteTypeDispatchSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query type dispatch success')


class SiteWithType:
    def __init__(self, id, long, lat, volume, avanum, box_type):
        self.id = id
        self.longitude = long
        self.latitude = lat
        self.volume = volume
        self.avanum = avanum
        self.type = box_type


def generate_dis_type():
    types = BoxTypeInfo.objects.all()
    for t in types:
        dsites = []
        sites = SiteInfo.objects.all()
        for site in sites:
            try:
                stock = SiteBoxStock.objects.get(site_id=site.id, box_type=t.id)
            except SiteBoxStock.DoesNotExist:
                continue
            dsite = SiteWithType(site.id, site.longitude, site.latitude, site.volume / 5, stock.ava_num, t.id)
            dsites.append(dsite)
        dispatch_type(dsites)
    return SiteTypeDispatch.objects.filter(create_date__gte=datetime.date.today()).order_by('did')


def divide_type(sites):
    low_sites = []
    high_sites = []
    ave_sites = []
    for site in sites:
        if site.avanum < site.volume * low:
            low_sites.append(site)
        elif site.avanum > site.volume * high:
            high_sites.append(site)
        else:
            ave_sites.append(site)
    return low_sites, high_sites, ave_sites


def dispatch_type(sites):
    low_sites, high_sites, ave_sites = divide_type(sites)
    if len(low_sites) > len(high_sites):
        high_sites += ave_sites

    for low_site in low_sites:
        dis_list = []
        if len(high_sites) == 0:
            break

        for high_site in high_sites:
            if high_site.type == low_site.type:
                dis = cal_distance(low_site, high_site)
                dis_list.append(dis)

        val, idx = min((val, idx) for (idx, val) in enumerate(dis_list))
        near_high_site = high_sites[idx]

        low_sites.remove(low_site)
        high_sites.remove(near_high_site)

        need_count = int(low_site.volume * ave) - low_site.avanum
        offer_count = near_high_site.avanum - int(near_high_site.volume * ave)

        if need_count < offer_count:
            count = need_count
        else:
            count = offer_count

        save_type_dispatch(near_high_site.id, low_site.id, near_high_site.type, count)


def save_type_dispatch(start_id, finish_id, type_id, count):
        try:
            did = generate_dispath_id()
            dispatch = SiteTypeDispatch(did=did, start_id=start_id, finish_id=finish_id, type_id = type_id, count=count,
                                    create_date=datetime.datetime.today())
            dispatch.save()
        except Exception, e:
            log.error(e.message)


def generate_dispath_id():
    type_code = '0'
    day = str(time.strftime('%Y%m%d', time.localtime(int(time.time()))))[3:]
    sql = '''select nextval('iot.monservice_dispatch_id_seq') from iot.monservice_dispatch_id_seq'''
    id_query = query_list(sql)
    seq = id_query[0][0]
    str_seq = '%06d' % seq
    ext_code = '0000'
    return  type_code + day + str_seq + ext_code


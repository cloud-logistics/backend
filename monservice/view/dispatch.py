#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
dispatch boxes between sites
'''

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.serializers import SiteInfoSerializer, SiteDispatchSerializer
import json
from monservice.models import SiteInfo, SiteDispatch, SiteBoxStock
from util import logger
from util.geo import get_distance
import datetime

log = logger.get_logger('monservice.dispatch.py')
low = 0.1
high = 0.9
ave = 0.5


@csrf_exempt
@api_view(['GET'])
def get_dispatches(request):
    try:

        dispatches = SiteDispatch.objects.filter(create_time__gte=datetime.date.today()).order_by('did')
        if len(dispatches) == 0:
            dispatches = generate_dispatches()
        ser_dispatches = SiteDispatchSerializer(dispatches)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'dispatches': ser_dispatches.data, 'status':'OK', 'msg': 'query dispatches success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DSite:
    def __init__(self, id, long, lat, volume, avanum):
        self.id = id
        self.long = long
        self.lat = lat
        self.volume = volume
        self.avanum = avanum


def generate_dispatches():
    dsites = []
    sites = SiteInfo.objects.all()
    for site in sites:
        stocks = SiteBoxStock.objects.filter(site_id=site.did)
        avanum = 0
        for stock in stocks:
            avanum = avanum + stock.ava_num
        dsite = DSite(site.did, site.longitude, site.latitude, site.volume, avanum)
        dsites.append(dsite)
    get_dispatch(dsites)
    return SiteDispatch.objects.filter(create_time__gte=datetime.date.today()).order_by('did')


def get_dispatch(sites):
    low_sites, high_sites, ave_sites = divide(sites)
    if len(low_sites) > len(high_sites):
        high_sites += ave_sites

    for low_site in low_sites:
        short_dis = 0.0
        index = 0
        for high_site in high_sites:
            dis = cal_distance(low_site, high_site)
            if index == 0:
                short_dis = dis
            else:
                if dis < short_dis:
                    short_dis = dis
                    index += 1
        near_high_site = high_sites[index]

        low_sites.remove(low_site)
        high_sites.remove(near_high_site)

        need_count = low_site.volume * ave - low_site.avanum
        offer_count = near_high_site.volume * high - near_high_site.avanum

        if need_count < offer_count:
            count = need_count
        else:
            count = low_site.volume.low
        save_dispatch(low_site.id, near_high_site.id, count)


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

        dispatch = SiteDispatch(start=start_site, finish=finish_site, count=count, create_date=datetime.datetime.today())
        dispatch.save()
    except Exception, e:
        log.error(e.message)






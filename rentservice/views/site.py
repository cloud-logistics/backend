#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from monservice.models import SiteInfo
from monservice.serializers import SiteInfoSerializer
from rentservice.utils.retcode import *
from rentservice.utils.logger import *
import uuid
import datetime
import pytz

log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')


@csrf_exempt
@api_view(['GET'])
def get_site_list(request, latitude, longitude):
    _lat = float(latitude)
    _lng = float(longitude)
    site_list = SiteInfo.objects.raw(
        '''select *, ROUND(6378.138*2*ASIN(SQRT(POW(SIN((%s*PI()/180-latitude::NUMERIC *PI()/180)/2),2) \
        +COS(%s*PI()/180)*COS(latitude::NUMERIC*PI()/180)*POW(SIN((%s*PI()/180-longitude::NUMERIC*PI()/180)/2),2)))*1000) AS juli\
        from monservice_siteinfo order by juli ASC
        ''', [_lat, _lat, _lng])
    return JsonResponse(retcode(SiteInfoSerializer(site_list, many=True).data, "000000", "Success"), safe=True,
                        status=status.HTTP_200_OK)

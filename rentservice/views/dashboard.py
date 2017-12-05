#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rentservice.models import EnterpriseInfo
from rentservice.models import SiteInfo
from rentservice.models import RentLeaseInfo
from rentservice.utils.retcode import *

import pytz
from django.conf import settings

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['GET'])
def get_dash_data(request):
    # 获取运输企业个数
    enterprise_count = EnterpriseInfo.objects.all().count()
    # 获取仓库的个数
    site_count = SiteInfo.objects.all().count()
    # 获取在运箱子的总数
    box_count = RentLeaseInfo.objects.filter(rent_status=0).count()
    ret = {'enterprise_count': enterprise_count, 'site_count': site_count, 'box_count': box_count}
    return JsonResponse(retcode(ret, "0000", "Success"), safe=True, status=status.HTTP_200_OK)

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rentservice.models import BoxRentFeeDetail, EnterpriseInfo
from rentservice.utils.retcode import retcode, errcode
from rentservice.utils import logger
from django.db.models import Sum
import pytz
from django.conf import settings


log = logger.get_logger(__name__)
timezone = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['GET'])
def box_bill_real_time_all(request):
    ret_list=[]
    enterprise_id_map = {}
    try:
        query_list = BoxRentFeeDetail.objects.select_related().values('enterprise').annotate(off_num=Sum('off_site_nums'),
                                                               on_num=Sum('on_site_nums'), fee=Sum('rent_fee'))
        enterprise_query_list = EnterpriseInfo.objects.all()
        for enterprise in enterprise_query_list:
            enterprise_id_map[enterprise.enterprise_id] = enterprise.enterprise_name
        for item in query_list:
            temp = {}
            temp['on_num']=item['on_num']
            temp['off_num'] = item['off_num']
            temp['fee'] = item['fee']
            temp['enterprise_id'] = item['enterprise']
            temp['enterprise_name'] = enterprise_id_map[item['enterprise']]
            ret_list.append(temp)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '云箱计费查询失败'), "0500", '云箱计费查询失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(ret_list, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


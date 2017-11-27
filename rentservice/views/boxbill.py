#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rest_framework.parsers import JSONParser
from rentservice.models import BoxRentFeeDetail, EnterpriseInfo, BoxRentFeeByMonth, RentLeaseInfo
from rentservice.utils.retcode import retcode, errcode
from rentservice.serializers import BoxRentFeeByMonthSerializer, RentLeaseInfoSerializer, EnterpriseInfoSerializer
from rentservice.utils import logger
from django.db.models import Sum
import pytz
from django.conf import settings
from django.db.models import Q


log = logger.get_logger(__name__)
timezone = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['GET'])
def box_bill_real_time_all(request):
    ret_list = []
    enterprise_id_map = {}
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        query_list = BoxRentFeeDetail.objects.select_related().values('enterprise').annotate(off_num=Sum('off_site_nums'),
                                                               on_num=Sum('on_site_nums'), fee=Sum('rent_fee'))
        enterprise_query_list = EnterpriseInfo.objects.all()
        for enterprise in enterprise_query_list:
            enterprise_id_map[enterprise.enterprise_id] = enterprise.enterprise_name
        for item in query_list:
            temp = {}
            temp['on_num'] = item['on_num']
            temp['off_num'] = item['off_num']
            temp['fee'] = item['fee']
            temp['enterprise_id'] = item['enterprise']
            temp['enterprise_name'] = enterprise_id_map[item['enterprise']]
            ret_list.append(temp)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '云箱计费查询失败'), "0500", '云箱计费查询失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    page = paginator.paginate_queryset(ret_list, request)
    return paginator.get_paginated_response(page)


@csrf_exempt
@api_view(['GET'])
def enterprise_month_bill(request, enterprise_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        box_rent_fee_month_bill = BoxRentFeeByMonth.objects.filter(enterprise=enterprise_id).order_by('-date')
    except BoxRentFeeByMonth.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '查询企业计费报表失败'), "0500", '查询企业计费报表失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    page = paginator.paginate_queryset(box_rent_fee_month_bill, request)
    ret_ser = BoxRentFeeByMonthSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['GET'])
def enterprise_month_bill_detail(request, enterprise_id, date):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        log.info("enterprise_id=%s, date=%s" % (enterprise_id, date))
        year = date.split('-')[0]
        month = int(date.split('-')[1])
        # if month <=0 or month >12:
        #     return JsonResponse(retcode(errcode("0400", '日期参数错误'), safe=True, status=status.HTTP_400_BAD_REQUEST)
        rent_info_list = RentLeaseInfo.objects.filter(user_id__enterprise__enterprise_id=enterprise_id,
                                                      lease_end_time__year=year, lease_end_time__month=month)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '查询企业月报表明细错误'), "0500", '查询企业月报表明细错误'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    page = paginator.paginate_queryset(rent_info_list, request)
    ret_ser = RentLeaseInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['POST'])
def box_bill_real_time_all_filter(request):
    ret_list = []
    enterprise_id_map = {}
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    data = JSONParser().parse(request)
    try:
        keyword = data['keyword']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '关键字为空'), "9999", '关键字为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    enterprise_all_list = EnterpriseInfo.objects.all()
    enterprise_id_list = EnterpriseInfo.objects.filter(Q(enterprise_name__contains=keyword)).values_list('enterprise_id', flat=True)
    try:
        query_list = BoxRentFeeDetail.objects.select_related().values('enterprise').annotate(off_num=Sum('off_site_nums'),
                                                               on_num=Sum('on_site_nums'), fee=Sum('rent_fee'))
        for enterprise in enterprise_all_list:
            enterprise_id_map[enterprise.enterprise_id] = enterprise.enterprise_name
        for item in query_list:
            temp = {}
            temp['on_num'] = item['on_num']
            temp['off_num'] = item['off_num']
            temp['fee'] = item['fee']
            temp['enterprise_id'] = item['enterprise']
            temp['enterprise_name'] = enterprise_id_map[item['enterprise']]
            if temp['enterprise_id'] in enterprise_id_list:
                ret_list.append(temp)
            else:
                continue
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '云箱计费查询失败'), "0500", '云箱计费查询失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    page = paginator.paginate_queryset(ret_list, request)
    return paginator.get_paginated_response(page)




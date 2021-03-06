#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rest_framework.parsers import JSONParser
from rentservice.models import BoxRentFeeDetail, EnterpriseInfo, BoxRentFeeByMonth, RentLeaseInfo
from monservice.models import City
from rentservice.utils.retcode import retcode, errcode
from rentservice.serializers import BoxRentFeeByMonthSerializer, RentLeaseInfoSerializer, EnterpriseInfoSerializer
from rentservice.utils import logger
from django.db.models import Sum
import pytz
from django.conf import settings
from django.db.models import Q
import datetime

log = logger.get_logger(__name__)
timezone = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['GET'])
def box_bill_real_time_all(request):
    ret_list = []
    current_time = datetime.datetime.now(tz=timezone)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        enterprise_query_list = EnterpriseInfo.objects.all()
        for enterprise in enterprise_query_list:
            rentlease_list = RentLeaseInfo.objects.filter(user_id__enterprise__enterprise_id=enterprise.enterprise_id)
            # rentlease_list = rentlease_list_with_today.exclude(lease_end_time__year=current_time.year,
            #                                                    lease_end_time__month=current_time.month,
            #                                                    lease_end_time__day=current_time.day)
            if rentlease_list:
                on_num = 0
                off_num = 0
                fee = 0
                bill = {}
                for item in rentlease_list:
                    if item.rent_status == 0 and (not item.lease_end_time):
                        off_num = off_num + 1
                    if item.lease_end_time \
                            and (item.lease_end_time.year == current_time.year) \
                            and (item.lease_end_time.month == current_time.month):
                        on_num = on_num + 1
                        fee = fee + item.rent
                bill['on_num'] = on_num
                bill['off_num'] = off_num
                bill['fee'] = fee
                bill['enterprise_id'] = enterprise.enterprise_id
                bill['enterprise_name'] = enterprise.enterprise_name
                ret_list.append(bill)
            else:
                continue
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
        box_rent_fee_month_bill = BoxRentFeeByMonth.objects.filter(enterprise=enterprise_id).order_by('date')
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
                                                      lease_end_time__year=year,
                                                      lease_end_time__month=month).order_by('-lease_end_time')
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '查询企业月报表明细错误'), "0500", '查询企业月报表明细错误'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    page = paginator.paginate_queryset(rent_info_list, request)
    ret_ser = RentLeaseInfoSerializer(page, many=True)
    for item in ret_ser.data:
        log.info("off city_code is %s" % item['off_site']['city'])
        log.info("on city_code is %s" % item['on_site']['city'])
        item['off_city'] = City.objects.get(id=item['off_site']['city']).city_name
        item['on_city'] = City.objects.get(id=item['on_site']['city']).city_name
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['POST'])
def box_bill_real_time_all_filter(request):
    ret_list = []
    current_time = datetime.datetime.now(tz=timezone)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    data = JSONParser().parse(request)
    try:
        keyword = data['keyword']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '关键字为空'), "9999", '关键字为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    log.info("input keyword is %s" % keyword)
    log.debug("input keyword type is %s" % type(keyword))
    enterprise_id_list = EnterpriseInfo.objects.filter(Q(enterprise_name__contains=keyword))
    enterprise_id_list_ser = EnterpriseInfoSerializer(enterprise_id_list, many=True)
    log.debug("enterprise_id_list is %s" % enterprise_id_list_ser.data)
    log.debug("current_time.year=%s, current_time.month=%s" % (current_time.year, current_time.month))
    try:
        for enterprise in enterprise_id_list:
            rentlease_list = RentLeaseInfo.objects.filter(user_id__enterprise__enterprise_id=enterprise.enterprise_id)
            # rentlease_list = rentlease_list_with_today.exclude(lease_end_time__year=current_time.year,
            #                                                    lease_end_time__month=current_time.month,
            #                                                    lease_end_time__day=current_time.day)
            if rentlease_list:
                on_num = 0
                off_num = 0
                fee = 0
                bill = {}
                for item in rentlease_list:
                    if item.rent_status == 0 and (not item.lease_end_time):
                        off_num = off_num + 1
                    if item.lease_end_time \
                        and (item.lease_end_time.year == current_time.year) \
                        and (item.lease_end_time.month == current_time.month):
                        on_num = on_num + 1
                        fee = fee + item.rent
                bill['on_num'] = on_num
                bill['off_num'] = off_num
                bill['fee'] = fee
                bill['enterprise_id'] = enterprise.enterprise_id
                bill['enterprise_name'] = enterprise.enterprise_name
                ret_list.append(bill)
            else:
                log.info("rentlease_list is null")
                continue
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '云箱计费查询失败'), "0500", '云箱计费查询失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    page = paginator.paginate_queryset(ret_list, request)
    return paginator.get_paginated_response(page)




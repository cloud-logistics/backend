#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import RentLeaseInfo, RentalServiceAdmin, EnterpriseUser
from rentservice.models import RentalAdminOperationRecords, AppointmentDetail, UserAppointment
from monservice.models import SiteInfo, BoxInfo, SiteBoxStock
from rentservice.utils.retcode import retcode, errcode
from rentservice.utils import logger
from django.db import transaction
import uuid
import datetime
import pytz

log = logger.get_logger(__name__)
timezone = pytz.timezone('Asia/Shanghai')


@csrf_exempt
@api_view(['POST'])
def rent_boxes_order(request):
    ret = {}
    data = JSONParser().parse(request)
    try:
        site_id = data['site_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '堆场id不能为空'), "9999", '堆场id不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        box_id_list = data['box_id_list']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '租赁云箱列表不能为空'), "9999", '租赁云箱列表不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        appoint_id = data['appoint_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '预约单id不能为空'), "9999", '预约单id不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        try:
            site = SiteInfo.objects.get(id=site_id)
        except SiteInfo.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '仓库不存在'), "9999", '仓库不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            user_appoint = UserAppointment.objects.get(appointment_id=appoint_id)
        except UserAppointment.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '预约单不存在'), "9999", '预约单不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            enterprise_user = EnterpriseUser.objects.get(user_id=user_appoint.user_id_id)
        except EnterpriseUser.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '预约单所属用户不存在'), "9999", '预约单所属用户不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        appoint_detail_queryset = AppointmentDetail.objects.filter(appointment_id=user_appoint, site_id=site)
        box_info_list = BoxInfo.objects.filter(ava_flag='Y', deviceid__in=box_id_list)
        lease_info_list = []
        with transaction.atomic():
            for item in box_info_list:
                lease_info = RentLeaseInfo(lease_info_id=uuid.uuid1(), user_id=enterprise_user,
                                           lease_start_time=datetime.datetime.now(tz=timezone), box=item, on_site=site)
                lease_info.save()
                #SiteBoxStock update
                site_box_stock = SiteBoxStock.objects.get(site=site, box_type=item.type)
                orig_ava_num = site_box_stock.ava_num
                orig_reserve_num = site_box_stock.reserve_num
                site_box_stock.ava_num = orig_ava_num - 1
                site_box_stock.reserve_num = orig_reserve_num - 1
                site_box_stock.save()
                lease_info_list.append(lease_info.lease_info_id)
            #结束预约
            for appoint_detail in appoint_detail_queryset:
                appoint_detail.flag = 1
                appoint_detail.save()
        ret['rent_lease_info_id_list'] = lease_info_list
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '租赁云箱失败'), "0500", '租赁云箱失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def finish_boxes_order(request):
    ret = {}
    data = JSONParser().parse(request)
    try:
        site_id = data['site_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '堆场id不能为空'), "9999", '堆场id不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        box_id_list = data['box_id_list']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '云箱列表不能为空'), "9999", '租赁云箱列表不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        try:
            site = SiteInfo.objects.get(id=site_id)
        except SiteInfo.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '仓库不存在'), "9999", '仓库不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        box_info_list = BoxInfo.objects.filter(ava_flag='Y', deviceid__in=box_id_list)
        rent_info_list = RentLeaseInfo.objects.filter(box_id__in=box_id_list, rent_status=0)
        for item in rent_info_list:
            item.rent_status = 1
            item.lease_end_time = datetime.datetime.now(tz=timezone)
            item.save()
        #update
        for item in box_info_list:
            site_box_stock = SiteBoxStock.objects.get(site=site, box_type=item.type)
            orig_ava_num = site_box_stock.ava_num
            site_box_stock.ava_num = orig_ava_num + 1
            site_box_stock.save()
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '归还云箱失败'), "0500", '归还云箱失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import RentLeaseInfo, EnterpriseUser
from rentservice.models import AppointmentDetail, UserAppointment
from monservice.models import SiteInfo, BoxInfo
from monservice.view.site import enter_leave_site
from rentservice.utils.retcode import retcode, errcode
from rentservice.utils import logger
from django.db import transaction
import uuid
import datetime
import pytz
from django.conf import settings
from .notify import create_notify
from cloudbox import celery

log = logger.get_logger(__name__)
timezone = pytz.timezone(settings.TIME_ZONE)


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
            user_appoint = UserAppointment.objects.get(appointment_id=appoint_id, flag=0)
        except UserAppointment.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '预约单不存在'), "9999", '预约单不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            enterprise_user = EnterpriseUser.objects.get(user_id=user_appoint.user_id_id)
        except EnterpriseUser.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '预约单所属用户不存在'), "9999", '预约单所属用户不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        appoint_detail_queryset = AppointmentDetail.objects.filter(appointment_id=user_appoint, site_id=site)
        # 所租云箱必须隶属于当前site，否则报错
        box_info_list = BoxInfo.objects.filter(ava_flag='Y', deviceid__in=box_id_list, siteinfo__id=site_id)
        log.info('box_id_list = %s, site_id = %s, query result list is %s' % (box_id_list, site_id, box_info_list))
        lease_info_list = []
        current_time = datetime.datetime.now(tz=timezone)
        with transaction.atomic():
            stock_data = {}
            stock_data['site_id'] = site_id
            box_para_list = []
            for item in box_info_list:
                lease_info = RentLeaseInfo(lease_info_id=uuid.uuid1(), user_id=enterprise_user,
                                           lease_start_time=current_time, box=item, off_site=site,
                                           last_update_time=current_time)
                lease_info.save()
                lease_info_list.append(lease_info.lease_info_id)
                box_para = {}
                box_para['box_id'] = item.deviceid
                box_para['type'] = 0
                box_para_list.append(box_para)
            # SiteBoxStock update
            stock_data['boxes'] = box_para_list
            enter_leave_site(stock_data)
            # 结束预约
            for appoint_detail in appoint_detail_queryset:
                appoint_detail.flag = 1
                appoint_detail.save()
            # 预约单更新为已完成
            user_appoint.flag = 1
            user_appoint.save()
        ret['rent_lease_info_id_list'] = lease_info_list
        # 增加消息
        alias = []
        alias.append(enterprise_user.user_alias_id)
        message = u'您的云箱已经租赁成功'
        celery.send_push_message.delay(alias, message)
        notify_message = u'您的云箱已经租赁成功，箱子ID分别是'
        for _box in box_info_list:
            notify_message += u' [ %s ] ' % _box.deviceid
        create_notify("云箱租赁", notify_message, enterprise_user.user_id)
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
        try:
            rent_info_list = RentLeaseInfo.objects.filter(box_id__in=box_id_list, rent_status=0)
        except RentLeaseInfo.DoesNotExist:
            return JsonResponse(retcode(errcode("9999", '租赁信息不存在'), "9999", '租赁信息不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        lease_info_list = []
        for item in rent_info_list:
            item.rent_status = 1
            item.lease_end_time = datetime.datetime.now(tz=timezone)
            rent_rate = get_rent_fee_rate(item)
            delta_datetime = item.lease_end_time - item.lease_start_time
            item.rent = (delta_datetime.days * 24 + delta_datetime.seconds / 3600) * rent_rate
            item.on_site = site
            lease_info_list.append(item.lease_info_id)
            item.save()
        # update
        stock_data = {}
        stock_data['site_id'] = site_id
        box_para_list = []
        for item in box_info_list:
            box_para = {}
            box_para['box_id'] = item.deviceid
            box_para['type'] = 1
            box_para_list.append(box_para)
        stock_data['boxes'] = box_para_list
        enter_leave_site(stock_data)
        # 增加消息
        alias = []
        alias.append(rent_info_list[0].user_id.user_alias_id)
        message = u'您的云箱已经归还成功'
        celery.send_push_message.delay(alias, message)
        notify_message = u'您的云箱已经归还成功，箱子ID分别是'
        for _box in box_info_list:
            notify_message += u' [ %s ] ' % _box.deviceid
        create_notify("云箱租赁", notify_message, rent_info_list[0].user_id.user_id)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '归还云箱失败'), "0500", '归还云箱失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    ret['rent_lease_info_id_list'] = lease_info_list
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


def get_rent_fee_rate(lease_info):
    if lease_info.rent_fee_rate == 0:
        price_per_hour = int(lease_info.box.type.price)
    else:
        price_per_hour = lease_info.rent_fee_rate
    return price_per_hour

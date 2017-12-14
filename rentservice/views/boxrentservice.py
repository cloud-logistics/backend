#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import RentLeaseInfo, EnterpriseUser
from rentservice.models import AppointmentDetail, UserAppointment, BoxRentFeeByMonth, BoxRentFeeDetail
from rentservice.models import EnterpriseInfo
from monservice.models import SiteInfo, BoxInfo, BoxTypeInfo, SiteBoxStock
from monservice.serializers import BoxTypeInfoSerializer, BoxInfoSerializer
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
        appoint_detail_queryset = AppointmentDetail.objects.filter(appointment_id=user_appoint, site_id=site, flag=0)
        if appoint_detail_queryset.count() == 0:
            return JsonResponse(retcode(errcode("9999", '没有可用预约单详情或预约单已完成'), "9999", '没有可用预约单详情或预约单已完成'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 所租云箱必须隶属于当前site，否则报错
        box_info_list = BoxInfo.objects.filter(ava_flag='Y', deviceid__in=box_id_list, siteinfo__id=site_id)
        if box_info_list.count() == 0:
            log.error("there is no available box in the site")
            log.info('box_id_list = %s, site_id = %s, query result list is %s' % (box_id_list, site_id,
                                                                                  BoxInfoSerializer(box_info_list, many=True).data))
            return JsonResponse(retcode(errcode("9999", '堆场没有符合条件的云箱'), "9999", '堆场没有符合条件的云箱'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        appoint_box_type_map = {}
        for detail in appoint_detail_queryset:
            if detail.box_type.id in appoint_box_type_map.keys():
                pass
            else:
                appoint_box_type_map[detail.box_type.id] = detail.box_num
        log.info("appoint_box_type_map = %s" % appoint_box_type_map)
        # map
        # key=box_type_id, value=num
        box_type_map = {}
        for box_id in box_info_list:
            try:
                box_info = BoxInfo.objects.get(deviceid=box_id.deviceid, siteinfo=site, ava_flag='Y',
                                               type__id__in=appoint_box_type_map.keys())
            except BoxInfo.DoesNotExist:
                log.error("BoxInfo.DoseNotExist box_id=%s, site=%s" % (box_id, site_id))
            if box_info:
                if box_info.type.id in box_type_map.keys():
                    orig = box_type_map[box_info.type.id]
                    box_type_map[box_info.type.id] = orig + 1
                else:
                    box_type_map[box_info.type.id] = 0
        for key in box_type_map.keys():
            stock = SiteBoxStock.objects.get(site=site, box_type__id=key)
            if stock.ava_num < box_type_map[key]:
                log.error("request box type stat is %s" % box_type_map)
                log.error("SiteBoxStock box_type=%s, ava_num=%s" % (key, stock.ava_num))
                return JsonResponse(retcode(errcode("9999", '堆场请求的云箱数目类型不匹配'), "9999", '堆场请求的云箱数目类型不匹配'), safe=True,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                continue
        log.info('box_id_list = %s, site_id = %s, query result list is %s' % (box_id_list, site_id,
                                                                              BoxInfoSerializer(box_info_list, many=True).data))
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
                stock = SiteBoxStock.objects.get(site=site, box_type=appoint_detail.box_type)
                orig_num = stock.reserve_num
                if orig_num >= appoint_detail.box_num:
                    stock.reserve_num = orig_num - appoint_detail.box_num
                    stock.save()
                else:
                    log.info("reserved_num less than appoint_detail.box_num")
            # 判断预约单状态是否完成
            if appoint_detail_queryset:
                unfinish_detail_counter = AppointmentDetail.objects.filter(appointment_id=appoint_detail_queryset[0].appointment_id, flag=0).count()
                if unfinish_detail_counter == 0:
                    user_appoint.flag = 1
                    user_appoint.save()
                else:
                    log.info("预约单还未全部完成")
        ret['rent_lease_info_id_list'] = lease_info_list
        # 增加消息
        if enterprise_user.user_alias_id is not None and enterprise_user.user_alias_id != "":
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
        if rent_info_list.count() == 0:
            return JsonResponse(retcode(errcode("9999", '租赁信息不存在或请求的云箱已归还'), "9999", '租赁信息不存在或请求的云箱已归还'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        lease_info_list = []
        box_para_list = []
        for item in rent_info_list:
            item.rent_status = 1
            item.lease_end_time = datetime.datetime.now(tz=timezone)
            rent_rate = get_rent_fee_rate(item)
            delta_datetime = item.lease_end_time - item.lease_start_time
            time_hours = (delta_datetime.days * 24 + delta_datetime.seconds / 3600)
            log.info("delta_datetime days=%s, seconds=%s" % (delta_datetime.days, delta_datetime.seconds))
            if time_hours:
                if delta_datetime.seconds % 3600:
                    item.rent = (time_hours + 1) * rent_rate
                else:
                    item.rent = time_hours * rent_rate
            else:
                #不足1小时按1小时算
                item.rent = rent_rate * 1
            item.on_site = site
            lease_info_list.append(item.lease_info_id)
            item.save()
            box_para = {}
            box_para['box_id'] = item.box.deviceid
            box_para['type'] = 1
            box_para_list.append(box_para)
        #update daily bill
        update_box_bill_daily()
        # update month bill
        update_box_bill_month()
        stock_data = {}
        stock_data['site_id'] = site_id
        stock_data['boxes'] = box_para_list
        enter_leave_site(stock_data)
        # 增加消息
        log.info("push message to app: begin")
        alias = []
        if rent_info_list:
            if rent_info_list[0].user_id.user_alias_id is not None and rent_info_list[0].user_id.user_alias_id != "":
                alias.append(rent_info_list[0].user_id.user_alias_id)
                message = u'您的云箱已经归还成功'
                celery.send_push_message.delay(alias, message)
            notify_message = u'您的云箱已经归还成功，箱子ID分别是'
            for _box in box_info_list:
                notify_message += u' [ %s ] ' % _box.deviceid
            create_notify("云箱租赁", notify_message, rent_info_list[0].user_id.user_id)
        else:
            log.info("rent_info_list is null, dont' push message")
        log.info("push message to app: end")
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("0500", '归还云箱失败'), "0500", '归还云箱失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    ret['rent_lease_info_id_list'] = lease_info_list
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def set_rent_fee_rate(request):
    data = JSONParser().parse(request)
    try:
        type_id = data['type_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '箱子类型不能为空'), "9999", '箱子类型不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        fee_per_hour = data['fee_per_hour']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '箱子租赁价格不能为空'), "9999", '箱子租赁价格不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        box_type_info = BoxTypeInfo.objects.get(id=type_id)
        box_type_info.price = float(fee_per_hour)
        box_type_info.save()
        ser_data = BoxTypeInfoSerializer(box_type_info)
    except BoxTypeInfo.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("9999", '修改云箱租赁价格失败'), "9999", '修改云箱租赁价格失败'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(ser_data.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def box_type_info_list(request):
    try:
        box_type_info_list = BoxTypeInfo.objects.all().order_by('id')
        ser_data = BoxTypeInfoSerializer(box_type_info_list, many=True)
    except e:
        log.error(repr(e))
    return JsonResponse(retcode(ser_data.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


def get_rent_fee_rate(lease_info):
    if lease_info.rent_fee_rate == 0:
        price_per_hour = int(lease_info.box.type.price)
    else:
        price_per_hour = lease_info.rent_fee_rate
    return price_per_hour


def update_box_bill_daily():
    current_time = datetime.datetime.now(tz=timezone)
    log.info("update_box_bill_daily: compute begin")
    try:
        user_list = RentLeaseInfo.objects.filter(rent_status=1, sum_flag=0).values_list('user_id', flat=True)
        user_obj_list = EnterpriseUser.objects.filter(user_id__in=user_list)
        log.info("update_box_bill_daily: user_list = %s" % user_list)
        for user in user_obj_list:
            off_site_counts = 0
            on_site_counts = RentLeaseInfo.objects.filter(user_id=user, rent_status=1, sum_flag=0).count()
            rent_lease_info_list = RentLeaseInfo.objects.filter(user_id=user, rent_status=1, sum_flag=0)
            user_rent_fee_sum = 0
            with transaction.atomic():
                for rent_lease_info in rent_lease_info_list:
                    user_rent_fee_sum = user_rent_fee_sum + rent_lease_info.rent
                    rent_lease_info.sum_flag = 1
                    rent_lease_info.last_update_time = current_time
                    rent_lease_info.save()
                log.info("update_box_bill_daily: off_site_counts=%s, on_site_counts=%s" % (off_site_counts, on_site_counts))
                box_rent_fee = BoxRentFeeDetail(detail_id=uuid.uuid1(), enterprise=user.enterprise,
                                                user=user, date=current_time,
                                                off_site_nums=off_site_counts,
                                                on_site_nums=on_site_counts, rent_fee=user_rent_fee_sum)
                box_rent_fee.save()
    except Exception, e:
        log.error(repr(e))
    log.info("update_box_bill_daily: compute finsih")


def update_box_bill_month():
    current_time = datetime.datetime.now(tz=timezone)
    if BoxRentFeeDetail.objects.all().count() > 0:
        log.info("box_rent_fee_month_billing: compute begin")
        try:
            enterprise_list = BoxRentFeeDetail.objects.values('enterprise').distinct()
            for enterprise in enterprise_list:
                enterprise_obj = EnterpriseInfo.objects.get(enterprise_id=enterprise['enterprise'])
                query_list = BoxRentFeeDetail.objects.filter(enterprise=enterprise_obj,
                                                             date__year=current_time.year,
                                                             date__month=current_time.month)
                off_site_box_nums_month = 0
                on_site_box_nums_month = 0
                rent_fee_month = 0
                for box_rent_day in query_list:
                    rent_fee_month = rent_fee_month + box_rent_day.rent_fee
                    on_site_box_nums_month = on_site_box_nums_month + box_rent_day.on_site_nums
                    off_site_box_nums_month = off_site_box_nums_month + box_rent_day.off_site_nums
                log.info("enterprise_id = %s, rent_fee_month=%s, on_site_box_nums_month=%s,off_site_box_nums_month=%s"
                         % (enterprise['enterprise'], rent_fee_month, on_site_box_nums_month, off_site_box_nums_month))
                try:
                    box_rent_bill_month = BoxRentFeeByMonth.objects.get(enterprise=enterprise_obj,
                                                                        date__year=current_time.year,
                                                                        date__month=current_time.month)
                    box_rent_bill_month.rent_fee = rent_fee_month
                    box_rent_bill_month.off_site_nums = off_site_box_nums_month
                    box_rent_bill_month.on_site_nums = on_site_box_nums_month
                    box_rent_bill_month.save()
                except BoxRentFeeByMonth.DoesNotExist, e:
                    month_date = datetime.datetime(current_time.year, current_time.month, 1)
                    box_rent_fee = BoxRentFeeByMonth(detail_id=uuid.uuid1(), enterprise=enterprise_obj,
                                                     date=month_date, off_site_nums=off_site_box_nums_month,
                                                     on_site_nums=on_site_box_nums_month,
                                                     rent_fee=rent_fee_month)
                    box_rent_fee.save()
                    log.error(repr(e))
        except Exception, e:
            log.error(repr(e))
        log.info("box_rent_fee_month_billing: compute finsih")
    else:
        log.info("no BoxRentFeeDetail records. do nothing")


#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.settings import api_settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rentservice.utils.retcode import *
from django.db import transaction
from rentservice.models import UserAppointment
from rentservice.models import AppointmentDetail
from monservice.models import SiteBoxStock
from rentservice.models import EnterpriseUser
from rentservice.models import AppointmentCodeSeq
from rentservice.serializers import UserAppointmentSerializer
from rentservice.serializers import AppointmentDetailSerializer
from monservice.models import SiteInfo
from monservice.models import BoxTypeInfo
from monservice.serializers import SiteInfoSerializer
from rentservice.serializers import AppointmentResSerializer
from django.conf import settings
import datetime
import uuid
import pytz
from cloudbox import celery

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


# 创建预约单
@csrf_exempt
@api_view(['POST'])
def create_appointment(request):
    data = JSONParser().parse(request)
    try:
        user_id = data['user_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入承运用户id"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        cancel_time = data['cancel_time']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入预约时间"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        site_total = data['site_total']
        if len(site_total) == 0:
            raise Exception
    except Exception:
        return JsonResponse(retcode({}, "9999", "堆场预约箱子数不能为空"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_model = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "承运方用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    try:
        with transaction.atomic():
            # 获取预约码
            code = get_appointment_code()
            # 生成预约单
            appointment_id = str(uuid.uuid1())
            # 获取取消时间
            _cancel_time = datetime.datetime.fromtimestamp(cancel_time)
            appointment_model = UserAppointment(appointment_id=appointment_id, appointment_code=code,
                                                appointment_time=datetime.datetime.today(), user_id=user_model,
                                                cancel_time=_cancel_time)
            appointment_model.save()
            # 循环获取每个堆场的请求
            detail_list = []
            for site in site_total:
                try:
                    site_id = site['site_id']
                except Exception:
                    raise Exception("堆场信息不能为空")
                site_model = SiteInfo.objects.get(id=site_id)
                # 获取堆场的可用数量信息
                try:
                    site_box_num = site['site_box_num']
                except Exception:
                    raise Exception("堆场可用箱子数量不能为空")
                for _site_num in site_box_num:
                    _stock_model = SiteBoxStock.objects.get(site=site_model, box_type=_site_num['box_type'])
                    # 根据可用数量-已经预约数量是否大于当前租借数量判断是否可租
                    if _site_num['num'] > _stock_model.ava_num - _stock_model.reserve_num:
                        raise Exception("预约数量大于堆场可用箱子数量")
                    # 更新box_type&site_id预约数量
                    upd_res_num = _stock_model.reserve_num + _site_num['num']
                    _stock_model.reserve_num = upd_res_num
                    _stock_model.save()
                    # 获取box_type的model
                    box_type_model = BoxTypeInfo.objects.get(id=_site_num['box_type'])
                    # 构建appointment_detail
                    appointment_detail = AppointmentDetail(detail_id=str(uuid.uuid1()),
                                                           appointment_id=appointment_model,
                                                           box_type=box_type_model, box_num=_site_num['num'],
                                                           site_id=site_model, flag=0)
                    detail_list.append(appointment_detail)
            # 批量insert appointment detail
            AppointmentDetail.objects.bulk_create(detail_list)
    except Exception as e:
        return JsonResponse(retcode({}, "9999", e.message), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    alias = []
    alias.append(user_model.user_alias_id)
    message = u'您的租箱预约已经成功，请到指定仓库获取云箱'
    celery.send_push_message.delay(alias, message)
    return JsonResponse(retcode(UserAppointmentSerializer(appointment_model).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 承运个人预约单查询
@csrf_exempt
@api_view(['GET'])
def get_list_by_user(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取预约单列表
    appointment_list = UserAppointment.objects.filter(user_id=user)
    ret = []
    for appointment_item in appointment_list:
        tmp_list = []
        res_app_list = []
        detail_list = AppointmentDetail.objects.filter(appointment_id=appointment_item)
        for detail in detail_list:
            if detail.site_id.id in tmp_list:
                # res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                #     AppointmentDetailSerializer(detail).data)
                res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                    detail)
            else:
                tmp_list.append(detail.site_id.id)
                # res_app_list.append({'site': SiteInfoSerializer(detail.site_id).data,
                #                      'box_info': [AppointmentDetailSerializer(detail).data]})
                res_app_list.append(
                    {'id': detail.site_id.id, 'location': detail.site_id.location, 'latitude': detail.site_id.latitude,
                     'longitude': detail.site_id.longitude, 'site_code': detail.site_id.site_code,
                     'city': detail.site_id.city, 'province': detail.site_id.province, 'nation': detail.site_id.nation,
                     'volume': detail.site_id.volume,
                     'box_info': [detail]})
        # ret.append({'appointment': UserAppointmentSerializer(appointment_item).data, 'info': res_app_list})

        ret.append({'appointment_id': appointment_item.appointment_id, 'user_id': appointment_item.user_id,
                    'appointment_time': appointment_item.appointment_time,
                    'appointment_code': appointment_item.appointment_code, 'flag': appointment_item.flag,
                    'info': res_app_list})
    page = paginator.paginate_queryset(ret, request)
    ret_ser = AppointmentResSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 进行中的预约单查询
@csrf_exempt
@api_view(['GET'])
def get_user_process_list(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取预约单列表
    appointment_list = UserAppointment.objects.filter(user_id=user, flag=0)
    ret = []
    for appointment_item in appointment_list:
        tmp_list = []
        res_app_list = []
        detail_list = AppointmentDetail.objects.filter(appointment_id=appointment_item, flag=0)
        for detail in detail_list:
            if detail.site_id.id in tmp_list:
                # res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                #     AppointmentDetailSerializer(detail).data)
                res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                    detail)
            else:
                tmp_list.append(detail.site_id.id)
                # res_app_list.append({'site': SiteInfoSerializer(detail.site_id).data,
                #                      'box_info': [AppointmentDetailSerializer(detail).data]})
                res_app_list.append(
                    {'id': detail.site_id.id, 'location': detail.site_id.location, 'latitude': detail.site_id.latitude,
                     'longitude': detail.site_id.longitude, 'site_code': detail.site_id.site_code,
                     'city': detail.site_id.city, 'province': detail.site_id.province, 'nation': detail.site_id.nation,
                     'volume': detail.site_id.volume,
                     'box_info': [detail]})
        # ret.append({'appointment': UserAppointmentSerializer(appointment_item).data, 'info': res_app_list})

        ret.append({'appointment_id': appointment_item.appointment_id, 'user_id': appointment_item.user_id,
                    'appointment_time': appointment_item.appointment_time,
                    'appointment_code': appointment_item.appointment_code, 'flag': appointment_item.flag,
                    'info': res_app_list})
    page = paginator.paginate_queryset(ret, request)
    ret_ser = AppointmentResSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 已完成的预约单查询
@csrf_exempt
@api_view(['GET'])
def get_user_finished_list(request, user_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取预约单列表
    appointment_list = UserAppointment.objects.filter(user_id=user).exclude(flag=0)
    ret = []
    for appointment_item in appointment_list:
        tmp_list = []
        res_app_list = []
        detail_list = AppointmentDetail.objects.filter(appointment_id=appointment_item, flag=0)
        for detail in detail_list:
            if detail.site_id.id in tmp_list:
                # res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                #     AppointmentDetailSerializer(detail).data)
                res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                    detail)
            else:
                tmp_list.append(detail.site_id.id)
                # res_app_list.append({'site': SiteInfoSerializer(detail.site_id).data,
                #                      'box_info': [AppointmentDetailSerializer(detail).data]})
                res_app_list.append(
                    {'id': detail.site_id.id, 'location': detail.site_id.location, 'latitude': detail.site_id.latitude,
                     'longitude': detail.site_id.longitude, 'site_code': detail.site_id.site_code,
                     'city': detail.site_id.city, 'province': detail.site_id.province, 'nation': detail.site_id.nation,
                     'volume': detail.site_id.volume,
                     'box_info': [detail]})
        # ret.append({'appointment': UserAppointmentSerializer(appointment_item).data, 'info': res_app_list})

        ret.append({'appointment_id': appointment_item.appointment_id, 'user_id': appointment_item.user_id,
                    'appointment_time': appointment_item.appointment_time,
                    'appointment_code': appointment_item.appointment_code, 'flag': appointment_item.flag,
                    'info': res_app_list})
    page = paginator.paginate_queryset(ret, request)
    ret_ser = AppointmentResSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 预约单详情查询detail
@csrf_exempt
@api_view(['GET'])
def get_appointment_detail(request, appointment_id):
    try:
        appointment = UserAppointment.objects.get(appointment_id=appointment_id)
    except UserAppointment.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "预约单不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    tmp_list = []
    res_app_list = []
    detail_list = AppointmentDetail.objects.filter(appointment_id=appointment)
    for detail in detail_list:
        if detail.site_id.id in tmp_list:
            res_app_list[tmp_list.index(detail.site_id.id)]['box_info'].append(
                AppointmentDetailSerializer(detail).data)
        else:
            tmp_list.append(detail.site_id.id)
            res_app_list.append({'site': SiteInfoSerializer(detail.site_id).data,
                                 'box_info': [AppointmentDetailSerializer(detail).data]})
    ret = {'appointment': UserAppointmentSerializer(appointment).data, 'info': res_app_list}
    return JsonResponse(retcode(ret, "0000", "Success"), safe=True, status=status.HTTP_200_OK)


# 取消预约
@csrf_exempt
@api_view(['POST'])
def cancel_appointment(request):
    data = JSONParser().parse(request)
    try:
        appointment = UserAppointment.objects.get(appointment_id=data['appointment_id'])
    except UserAppointment.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "预约单不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # 获取预约单详情，并根据预约单详情将已经预留的数量回退
    detail_list = AppointmentDetail.objects.filter(appointment_id=appointment)
    try:
        with transaction.atomic():
            # 根据detail更新site stock的数量
            for detail in detail_list:
                stock = SiteBoxStock.objects.get(site=detail.site_id, box_type=detail.box_type)
                stock.reserve_num -= detail.box_num
                stock.save()
            # 更新appointment的flag为2（已取消）
            appointment.flag = 2
            appointment.save()
    except Exception as e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "9999", "取消预约失败"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(UserAppointmentSerializer(appointment).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 获取预约码
def get_appointment_code():
    appointment = AppointmentCodeSeq.objects.raw(
        "SELECT sequence_name,to_char(now(),'YYYYMMDD')||lpad(nextval('iot.appointment_code')::TEXT,8,'0') as code from iot.appointment_code")[
        0]
    return appointment.code

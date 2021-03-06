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
from .notify import create_notify
import datetime
import uuid
import pytz
from cloudbox import celery
from rentservice.utils import complex_page
from rentservice.utils.redistools import RedisTool
import pickle
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rentservice.models import EnterpriseInfo

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

APPOINTMENT_HASH = 'appointment'
USER_ALIAS_ID_HASH = 'user_alias_id_hash'
CANCEL_HASH = 'cancel_hash'


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
        appointment_time = data['appointment_time']
    except Exception:
        return JsonResponse(retcode({}, "9999", "预约时间不能为空"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_model = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "承运方用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    if user_model.enterprise.enterprise_deposit_status == 0:
        return JsonResponse(retcode({}, "9999", "企业未缴押金，无法预约租箱"), safe=True,
                            status=status.HTTP_200_OK)
    try:
        with transaction.atomic():
            # 获取预约码
            code = get_appointment_code()
            # 生成预约单
            appointment_id = str(uuid.uuid1())
            # 获取取消时间
            _cancel_time = datetime.datetime.fromtimestamp(cancel_time)
            _appointment_time = datetime.datetime.fromtimestamp(appointment_time)
            appointment_model = UserAppointment(appointment_id=appointment_id, appointment_code=code,
                                                appointment_time=_appointment_time, user_id=user_model,
                                                cancel_time=_cancel_time)
            appointment_model.save()
            # 循环获取每个堆场的请求
            detail_list = []
            for site in site_total:
                try:
                    site_id = site['site_id']
                except Exception:
                    raise Exception("9999", "堆场信息不能为空")
                site_model = SiteInfo.objects.get(id=site_id)
                # 获取堆场的可用数量信息
                try:
                    site_box_num = site['site_box_num']
                except Exception:
                    raise Exception("9999", "堆场可用箱子数量不能为空")
                for _site_num in site_box_num:
                    _stock_model = SiteBoxStock.objects.select_for_update().get(site=site_model,
                                                                                box_type=_site_num['box_type'])
                    # 根据可用数量-已经预约数量是否大于当前租借数量判断是否可租
                    if _site_num['num'] > _stock_model.ava_num - _stock_model.reserve_num:
                        raise Exception("9999", "预约数量大于堆场可用箱子数量")
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
        code, msg = e.args
        if code == '0000':
            return JsonResponse(retcode({}, code, msg), safe=True, status=status.HTTP_200_OK)
        else:
            return JsonResponse(retcode({}, code, msg), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    message = u'您的租箱预约已经成功，请到指定仓库获取云箱'
    create_notify("云箱预约", message, user_id)
    conn = get_connection_from_pool()
    user_id = user_model.user_id
    # if user_model.user_alias_id is not None and user_model.user_alias_id != "":
    if conn.hexists(USER_ALIAS_ID_HASH, user_id):
        alias = []
        # alias.append(user_model.user_alias_id)
        alias.append(conn.hget(USER_ALIAS_ID_HASH, user_id))
        celery.send_push_message.delay(alias, message)
    return JsonResponse(retcode(UserAppointmentSerializer(appointment_model).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 承运个人预约单查询
@csrf_exempt
@api_view(['GET'])
def get_list_by_user(request, user_id):
    # pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    pagination_class = complex_page.ComplexPagination
    param = request.query_params
    _limit = 10
    _offset = 0
    if param:
        _limit = int(param.get('limit'))
        _offset = int(param.get('offset'))
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取预约单列表
    _new_limit = _offset + _limit
    appointment_list = UserAppointment.objects.filter(user_id=user).order_by('-appointment_time')[_offset:_new_limit]
    _count = UserAppointment.objects.filter(user_id=user).count()
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
    paginator.paginate_queryset(ret, request, _count)
    ret_ser = AppointmentResSerializer(ret, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 进行中的预约单查询
@csrf_exempt
@api_view(['GET'])
def get_user_process_list(request, user_id):
    # pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    pagination_class = complex_page.ComplexPagination
    param = request.query_params
    _limit = 10
    _offset = 0
    if param:
        _limit = int(param.get('limit'))
        _offset = int(param.get('offset'))
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取预约单列表
    _new_limit = _offset + _limit
    appointment_list = UserAppointment.objects.filter(user_id=user, flag=0).order_by('-appointment_time')[
                       _offset:_new_limit]
    _count = UserAppointment.objects.filter(user_id=user, flag=0).count()
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
    paginator.paginate_queryset(ret, request, _count)
    ret_ser = AppointmentResSerializer(ret, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 已完成的预约单查询
@csrf_exempt
@api_view(['GET'])
@cache_page(CACHE_TTL)
def get_user_finished_list(request, user_id):
    # pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    pagination_class = complex_page.ComplexPagination
    param = request.query_params
    _limit = 10
    _offset = 0
    if param:
        _limit = int(param.get('limit'))
        _offset = int(param.get('offset'))
    paginator = pagination_class()
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "用户不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    # 获取预约单列表
    # appointment_list = UserAppointment.objects.filter(user_id=user).exclude(flag=0).order_by('-appointment_time')
    _new_limit = _offset + _limit
    appointment_list = UserAppointment.objects.filter(user_id=user).exclude(flag=0).order_by('-appointment_time')[
                       _offset:_new_limit]
    _count = UserAppointment.objects.filter(user_id=user).exclude(flag=0).count()
    conn = get_connection_from_pool()
    ret = []
    for appointment_item in appointment_list:
        if conn.hexists(APPOINTMENT_HASH, appointment_item.appointment_id):
            detail_pickle = conn.hget(APPOINTMENT_HASH, appointment_item.appointment_id)
            detail_dict = pickle.loads(detail_pickle)
        else:
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
                        {'id': detail.site_id.id, 'location': detail.site_id.location,
                         'latitude': detail.site_id.latitude,
                         'longitude': detail.site_id.longitude, 'site_code': detail.site_id.site_code,
                         'city': detail.site_id.city, 'province': detail.site_id.province,
                         'nation': detail.site_id.nation,
                         'volume': detail.site_id.volume,
                         'box_info': [detail]})
            # ret.append({'appointment': UserAppointmentSerializer(appointment_item).data, 'info': res_app_list})
            detail_dict = {'appointment_id': appointment_item.appointment_id, 'user_id': appointment_item.user_id,
                           'appointment_time': appointment_item.appointment_time,
                           'appointment_code': appointment_item.appointment_code, 'flag': appointment_item.flag,
                           'info': res_app_list}
            detail_pickle = pickle.dumps(detail_dict)
            conn.hset(APPOINTMENT_HASH, appointment_item.appointment_id, detail_pickle)
        ret.append(detail_dict)
    paginator.paginate_queryset(ret, request, _count)
    ret_ser = AppointmentResSerializer(ret, many=True)
    # page = paginator.paginate_queryset(ret, request)
    # ret_ser = AppointmentResSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 预约单详情查询detail
@csrf_exempt
@api_view(['GET'])
def get_appointment_detail(request, appointment_code):
    try:
        appointment = UserAppointment.objects.get(appointment_code=appointment_code, flag=0)
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


# 预约单详情查询detail,有site作为查询条件
@csrf_exempt
@api_view(['GET'])
def get_appointment_detail_by_site(request, appointment_code, site_id):
    try:
        appointment = UserAppointment.objects.get(appointment_code=appointment_code, flag=0)
    except UserAppointment.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "预约单不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    try:
        site = SiteInfo.objects.get(id=site_id)
    except SiteInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "仓库信息不存在"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    tmp_list = []
    res_app_list = []
    detail_list = AppointmentDetail.objects.filter(appointment_id=appointment, site_id=site)
    if len(detail_list) == 0:
        return JsonResponse(retcode({}, "9999", "未找到对应仓库的预约信息"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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


# 预约单详情查询detail
@csrf_exempt
@api_view(['GET'])
def get_appointment_detail_by_id(request, appointment_id):
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
        appointment = UserAppointment.objects.get(appointment_id=data['appointment_id'], flag=0)
    except UserAppointment.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "预约单不存在或已取消"), safe=True, status=status.HTTP_200_OK)
    # 获取预约单详情，并根据预约单详情将已经预留的数量回退
    detail_list = AppointmentDetail.objects.select_related('appointment_id', 'box_type').filter(
        appointment_id=appointment, flag=0)
    redis_update_content = {}
    conn = get_connection_from_pool()
    try:
        with transaction.atomic():
            # 根据detail更新site stock的数量
            for detail in detail_list:
                # stock = SiteBoxStock.objects.select_for_update().get(site=detail.site_id, box_type=detail.box_type)
                # stock.reserve_num -= detail.box_num
                # stock.save()
                redis_update_content['site'] = detail.site_id_id
                redis_update_content['box_type'] = detail.box_type.id
                redis_update_content['box_num'] = detail.box_num
                conn.rpush(CANCEL_HASH, json.dumps(redis_update_content))
                detail.flag = 1
                detail.save()
            # 更新appointment的flag为2（已取消）
            appointment.flag = 2
            appointment.save()
    except Exception as e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "9999", "取消预约失败"), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(UserAppointmentSerializer(appointment).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 获取企业预约单list
@csrf_exempt
@api_view(['POST'])
def get_enterprise_appointment(request):
    data = JSONParser().parse(request)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入企业用户id"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        keyword = data['keyword']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入keyword"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "企业信息不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    _appointment = UserAppointment.objects
    if keyword != "":
        _appointment = _appointment.filter(appointment_code__contains=keyword)
    ret = _appointment.filter(user_id__enterprise=enterprise).order_by("-appointment_code")
    page = paginator.paginate_queryset(ret, request)
    ret_ser = UserAppointmentSerializer(page, many=True)
    return paginator.get_paginated_response(ret_ser.data)


# 获取预约单detail信息
@csrf_exempt
@api_view(['GET'])
def get_enterprise_appointment_detail(request, appointment_id):
    try:
        appointment = UserAppointment.objects.get(appointment_id=appointment_id)
    except UserAppointment.DoesNotExist:
        return JsonResponse(retcode({}, "9999", "预约单不存在"), safe=True, status=status.HTTP_404_NOT_FOUND)
    ret = AppointmentDetail.objects.filter(appointment_id=appointment)
    return JsonResponse(retcode(AppointmentDetailSerializer(ret, many=True).data, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


# 获取预约码
def get_appointment_code():
    appointment = AppointmentCodeSeq.objects.raw(
        "SELECT sequence_name,to_char(now(),'YYYYMMDD')||lpad(nextval('iot.appointment_code')::TEXT,8,'0') as code from iot.appointment_code")[
        0]
    return appointment.code


def get_connection_from_pool():
    redis_pool = RedisTool()
    return redis_pool.get_connection()

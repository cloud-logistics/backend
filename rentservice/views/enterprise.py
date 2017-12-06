#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rest_framework.parsers import JSONParser
from rentservice.models import EnterpriseInfo, EnterpriseUser
from rentservice.utils.retcode import retcode, errcode
from rentservice.utils import logger
from ..serializers import EnterpriseInfoSerializer, EnterpriseUserSerializer
import uuid
import datetime
import pytz
from django.conf import settings
from django.db.models import Q

log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['POST'])
def add_enterprise_info(request):
    data = JSONParser().parse(request)
    try:
        enterprise_name = data['enterprise_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业名称不能为空'), "9999", '企业名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_tele = data['enterprise_tele']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业联系电话不能为空'), "9999", '企业联系电话不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id = data['enterprise_license_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业营业执照序号不能为空'), "9999", '企业营业执照序号不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_legal_rep_name = data['enterprise_legal_rep_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业法人名称不能为空'), "9999", '企业法人名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_deposit = data['enterprise_deposit']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业保证金不能为空'), "9999", '企业保证金不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_email = data['enterprise_email']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业邮箱不能为空'), "9999", '企业邮箱不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id_url = data['enterprise_license_id_url']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业营业执照照片url不能为空'), "9999", '企业营业执照照片url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_info = EnterpriseInfo(enterprise_id=uuid.uuid1(), enterprise_name=enterprise_name,
                                         enterprise_tele=enterprise_tele, enterprise_license_id=enterprise_license_id,
                                         enterprise_license_id_url=enterprise_license_id_url,
                                         enterprise_legal_rep_name=enterprise_legal_rep_name,
                                         enterprise_email=enterprise_email, enterprise_deposit=enterprise_deposit,
                                         enterprise_deposit_status=0, register_time=datetime.datetime.now(tz),
                                         last_update_time=datetime.datetime.now(tz))
        enterprise_info.save()
    except Exception, e:
        log.error(repr(e))
    ret = {}
    ret['enterprise_id'] = enterprise_info.enterprise_id
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def update_enterprise_info(request):
    data = JSONParser().parse(request)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业id为空'), "9999", '企业id为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_name = data['enterprise_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业名称不能为空'), "9999", '企业名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_tele = data['enterprise_tele']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业联系电话不能为空'), "9999", '企业联系电话不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id = data['enterprise_license_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业营业执照序号不能为空'), "9999", '企业营业执照序号不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_legal_rep_name = data['enterprise_legal_rep_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业法人名称不能为空'), "9999", '企业法人名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_deposit = data['enterprise_deposit']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业保证金不能为空'), "9999", '企业保证金不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_email = data['enterprise_email']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业邮箱不能为空'), "9999", '企业邮箱不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id_url = data['enterprise_license_id_url']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业营业执照照片url不能为空'), "9999", '企业营业执照照片url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_homepage_url = data['enterprise_homepage_url']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业网址不能为空'), "9999", '企业网址不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_address = data['enterprise_address']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业地址不能为空'), "9999", '企业地址不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    ret = {}
    ret['enterprise_id'] = enterprise_id
    try:
        enterprise_edit = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
        enterprise_edit.enterprise_name = enterprise_name
        enterprise_edit.enterprise_tele = enterprise_tele
        enterprise_edit.enterprise_license_id = enterprise_license_id
        enterprise_edit.enterprise_license_id_url = enterprise_license_id_url
        enterprise_edit.enterprise_legal_rep_name = enterprise_legal_rep_name
        enterprise_edit.enterprise_email = enterprise_email
        enterprise_edit.enterprise_deposit = enterprise_deposit
        enterprise_edit.last_update_time = datetime.datetime.now(tz)
        enterprise_edit.enterprise_homepage_url = enterprise_homepage_url
        enterprise_edit.enterprise_address = enterprise_address
        enterprise_edit.save()
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", '请求修改的企业信息不存在'), "9999", '请求修改的企业信息不存在'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", 'Succ'), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
def del_enterpise_info(request, enterprise_id):
    ret = {}
    try:
        EnterpriseInfo.objects.get(enterprise_id=enterprise_id).delete()
        ret['enterprise_id'] = enterprise_id
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", "删除企业信息失败"), "9999", "删除企业信息失败"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def list_enterpise_info(request):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        enterprise_ret = EnterpriseInfo.objects.all().order_by('-last_update_time')
        page = paginator.paginate_queryset(enterprise_ret, request)
        ret_ser = EnterpriseInfoSerializer(page, many=True)
    except Exception:
        return JsonResponse(retcode(errcode("9999", "查询企业信息列表失败"), "9999", "查询企业信息列表失败"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return paginator.get_paginated_response(ret_ser.data)


@csrf_exempt
@api_view(['GET'])
def enterpise_info_detail(request, enterprise_id):
    try:
        ret_enterpriseinfo = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
        ser_enterpriseinfo = EnterpriseInfoSerializer(ret_enterpriseinfo)
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", "查询企业信息失败"), "9999", "查询企业信息失败"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ser_enterpriseinfo.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
def enterpise_deposit_confirm(request):
    data = JSONParser().parse(request)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业id为空'), "9999", '企业id为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        ret_enterpriseinfo = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
        ser_enterpriseinfo = EnterpriseInfoSerializer(ret_enterpriseinfo)
        ret_enterpriseinfo.enterprise_deposit_status = 1
        ret_enterpriseinfo.save()
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", "查询企业信息失败"), "9999", "查询企业信息失败"), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ser_enterpriseinfo.data, "0000", "Succ"), safe=False, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def enterprise_fuzzy_query(request):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    data = JSONParser().parse(request)
    try:
        keyword = data['keyword']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '关键字为空'), "9999", '关键字为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    enterprise_data = EnterpriseInfo.objects.filter(Q(enterprise_name__contains=keyword)).order_by('register_time')
    page = paginator.paginate_queryset(enterprise_data, request)
    ser_ret = EnterpriseInfoSerializer(page, many=True)
    return paginator.get_paginated_response(ser_ret.data)


@csrf_exempt
@api_view(['POST'])
def enterpriseuser_fuzzy_query(request):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    data = JSONParser().parse(request)
    try:
        keyword = data['keyword']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '关键字为空'), "9999", '关键字为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业id为空'), "9999", '企业id为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    user_data = EnterpriseUser.objects.filter(Q(user_name__contains=keyword), enterprise_id=enterprise_id).order_by('register_time')
    page = paginator.paginate_queryset(user_data, request)
    ser_ret = EnterpriseUserSerializer(page, many=True)
    return paginator.get_paginated_response(ser_ret.data)
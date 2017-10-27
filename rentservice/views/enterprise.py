#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import EnterpriseInfo
from rentservice.utils.retcode import *
from rentservice.utils.logger import *
import uuid
import datetime
import pytz


log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')

@csrf_exempt
@api_view(['POST'])
def add_enterprise_info(request):
    data = JSONParser().parse(request)
    print request.get_full_path()
    try:
        enterprise_name = data['enterprise_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_tele = data['enterprise_tele']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业联系电话不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id = data['enterprise_license_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业营业执照序号不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_legal_rep_name = data['enterprise_legal_rep_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业法人名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_deposit = data['enterprise_deposit']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业保证金不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_email = data['enterprise_email']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业邮箱不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id_url = data['enterprise_license_id_url']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业营业执照照片url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_info = EnterpriseInfo(enterprise_id=uuid.uuid1(), enterprise_name=enterprise_name,
                                         enterprise_tele=enterprise_tele, enterprise_license_id=enterprise_license_id,
                                         enterprise_license_id_url=enterprise_license_id_url,
                                         enterprise_legal_rep_name=enterprise_legal_rep_name,
                                         enterprise_email=enterprise_email, enterprise_deposit=enterprise_deposit,
                                         enterprise_deposit_status=0, register_time=datetime.datetime.now(tz))
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
        return JsonResponse(retcode({}, "9999", '企业id为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_name = data['enterprise_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_tele = data['enterprise_tele']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业联系电话不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id = data['enterprise_license_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业营业执照序号不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_legal_rep_name = data['enterprise_legal_rep_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业法人名称不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_deposit = data['enterprise_deposit']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业保证金不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_email = data['enterprise_email']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业邮箱不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_license_id_url = data['enterprise_license_id_url']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业营业执照照片url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
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
        enterprise_edit.save()
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(ret, "9999", '请求修改的企业信息不存在'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", 'Succ'), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
def del_enterpise_info(request, enterprise_id):
    try:
        EnterpriseInfo.objects.get(enterprise_id=enterprise_id).delete()
        ret = {}
        ret['enterprise_id'] = enterprise_id
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(ret, "9999", "删除企业信息失败"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)



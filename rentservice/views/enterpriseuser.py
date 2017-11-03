#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import EnterpriseInfo, EnterpriseUser, AccessGroup, AuthUserGroup
from rentservice.utils.retcode import retcode, errcode
from rentservice.utils import logger
from rentservice.utils.redistools import RedisTool
from django.db import transaction
from rest_framework.settings import api_settings
from rentservice.serializers import EnterpriseUserSerializer
import uuid
import datetime
import pytz


log = logger.get_logger(__name__)
tz = pytz.timezone('Asia/Shanghai')
PERMISSION_GROUP_HASH = 'permissions_group_hash'
# PERMISSION_URL_HASH = 'permissions_url_hash'


@csrf_exempt
@api_view(['POST'])
def add_enterprise_user(request):
    ret = {}
    data = JSONParser().parse(request)
    try:
        user_name = data['user_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册姓名不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_password = data['user_password']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册密码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        avatar_url = data['avatar_url']
    except Exception:
        return JsonResponse(retcode({}, "9999", '头像url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_phone = data['user_phone']
    except Exception:
        return JsonResponse(retcode({}, "9999", '用户号码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_email = data['user_email']
    except Exception:
        return JsonResponse(retcode({}, "9999", '用户邮件地址不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业信息id不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        role = data['role']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业用户角色不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        group = data['group']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业用户所属群组不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        try:
            enterprise = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
        except EnterpriseUser.DoesNotExist:
            return JsonResponse(retcode({}, "9999", '企业信息id不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            group_obj = AccessGroup.objects.get(group=group)
        except AccessGroup.DoesNotExist:
            return JsonResponse(retcode({}, "9999", '企业用户群组不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            usr = EnterpriseUser.objects.get(user_name=user_name)
            if usr:
                log.error("Enterprise User exists already and return 500 error")
                return JsonResponse(retcode({}, "0500", '用户名已存在'), safe=True,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except EnterpriseUser.DoesNotExist:
                with transaction.atomic():
                    new_user = EnterpriseUser(user_id=uuid.uuid1(), user_name=user_name, user_password=user_password,
                                              status='', avatar_url=avatar_url, user_phone=user_phone,
                                              user_email=user_email, register_time=datetime.datetime.now(tz=tz),
                                              enterprise=enterprise, user_token=uuid.uuid4().hex, role=role,
                                              group=group_obj)
                    new_user.save()
                    auth_user_group = AuthUserGroup(user_token=new_user.user_token, group=group_obj)
                    auth_user_group.save()
                ret['user_id'] = new_user.user_id
                update_redis_token(new_user.user_token, group)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "0500", '创建用户失败'), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def update_enterprise_user(request):
    ret = {}
    data = JSONParser().parse(request)
    try:
        user_name = data['user_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册姓名不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_password = data['user_password']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册密码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        avatar_url = data['avatar_url']
    except Exception:
        return JsonResponse(retcode({}, "9999", '头像url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_phone = data['user_phone']
    except Exception:
        return JsonResponse(retcode({}, "9999", '用户号码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_email = data['user_email']
    except Exception:
        return JsonResponse(retcode({}, "9999", '用户邮件地址不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业信息id不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_id = data['user_id']
    except Exception:
        return JsonResponse(retcode({}, "9999", '修改用户id不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
        enterprise = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
        user.user_name = user_name
        user.user_password = user_password
        user.avatar_url = avatar_url
        user.user_phone = user_phone
        user.user_email = user_email
        user.enterprise_id = enterprise
        user.save()
    except EnterpriseUser.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(ret, "9999", '请求修改的企业用户信息不存在'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    ret={}
    ret['user_id'] = user.user_id
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
def del_enterprise_user(request, user_id):
    try:
        with transaction.atomic():
            del_user = EnterpriseUser.objects.get(user_id=user_id)
            AuthUserGroup.objects.get(user_token=del_user.user_token).delete()
            del_user.delete()
        ret = {}
        ret['user_id'] = user_id
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode(ret, "9999", "删除用户信息失败"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def list_enterprise_user(request):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        enterpise_user_ret = EnterpriseUser.objects.all()
        page = paginator.paginate_queryset(enterpise_user_ret, request)
        enterprise_user_ser = EnterpriseUserSerializer(page, many=True)
    except Exception, e:
        log.error(repr(e))
    return paginator.get_paginated_response(enterprise_user_ser.data)


@csrf_exempt
@api_view(['GET'])
def enterprise_user_detail(request, user_id):
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
        ser_user = EnterpriseUserSerializer(user)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", "查询用户信息失败"), "9999", "查询用户信息失败"), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ser_user.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


def update_redis_token(user_token, group):
    try:
        conn = get_connection_from_pool()
        ret = conn.hset(PERMISSION_GROUP_HASH, user_token, group)
    except Exception, e:
        log.error(repr(e))
    return ret


def del_redis_token(user_token):
    try:
        conn = get_connection_from_pool()
        ret = conn.hdel(PERMISSION_GROUP_HASH, user_token)
    except Exception, e:
        log.error(repr(e))
    return ret


def get_connection_from_pool():
    redis_pool = RedisTool()
    return redis_pool.get_connection()

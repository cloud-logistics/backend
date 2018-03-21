#! /usr/bin/env python
# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from tms.models import User, AccessGroup, AuthUserGroup, Role
from tms.utils.retcode import retcode, errcode
from tms.utils.logger import get_logger
from rentservice.utils.redistools import RedisTool
from rest_framework.settings import api_settings
from tms.serializers import UserSerializer
from django.db import transaction
from django.conf import settings
import hashlib
import uuid
import datetime
import pytz

log = get_logger(__name__)
PERMISSION_GROUP_HASH = 'tms_permissions_group_hash'
tz = pytz.timezone(settings.TIME_ZONE)


@csrf_exempt
@api_view(['GET'])
def list_users(request, role_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        list_fisher_ret = User.objects.filter(role__role_id=role_id)
        page = paginator.paginate_queryset(list_fisher_ret, request)
        user_ser = UserSerializer(page, many=True)
    except Exception, e:
        log.error(repr(e))
    return paginator.get_paginated_response(user_ser.data)


@csrf_exempt
@api_view(['GET'])
def user_detail(request, user_id):
    try:
        ret_user = User.objects.get(user_id=user_id)
        user_ser = UserSerializer(ret_user)
    except User.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(errcode("9999", "查询用户信息失败"), "9999", "查询用户信息失败"), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(user_ser.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def add_user(request):
    ret = {}
    data = JSONParser().parse(request)
    try:
        user_name = data['user_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '注册登陆名不能为空'), "9999", '注册登陆名不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_real_name = data['user_real_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '注册用户姓名不能为空'), "9999", '注册用户姓名不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_gender = data['user_gender']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '注册用户性别不能为空'), "9999", '注册用户性别不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_phone = data['user_phone']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册用户号码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        role = data['role']
        role_obj = Role.objects.get(role_id=role)
    except Exception:
        return JsonResponse(retcode({}, "9999", '用户角色不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    group_default = 'user'
    try:
        try:
            group_obj = AccessGroup.objects.get(group=group_default)
        except AccessGroup.DoesNotExist:
            return JsonResponse(retcode({}, "9999", '企业用户群组不存在'), safe=True,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            usr = User.objects.get(user_name=user_name)
            if usr:
                log.error("Enterprise User exists already and return 500 error")
                return JsonResponse(retcode({}, "0500", '登陆名已存在'), safe=True,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except User.DoesNotExist:
                with transaction.atomic():
                    md = hashlib.md5()
                    md.update('hna123')
                    md5_pwd = md.hexdigest()
                    new_user = User(user_id=uuid.uuid1(), user_name=user_name, user_password='hna123',
                                              status='', avatar_url='', user_phone=user_phone,
                                              user_email='', register_time=datetime.datetime.now(tz=tz),
                                              user_token=uuid.uuid4().hex, role=role_obj,
                                              group=group_obj, user_real_name=user_real_name, user_gender=user_gender,
                                              user_alias_id=uuid.uuid1().hex, user_password_encrypt=md5_pwd)
                    new_user.save()
                    auth_user_group = AuthUserGroup(user_token=new_user.user_token, group=group_obj)
                    auth_user_group.save()
                ret['user_id'] = new_user.user_id
                update_redis_token(new_user.user_token, group_default)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "0500", '创建用户失败'), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
def del_user(request, user_id):
    try:
        with transaction.atomic():
            del_user = User.objects.get(user_id=user_id)
            try:
                auth_user_relation = AuthUserGroup.objects.get(user_token=del_user.user_token)
                auth_user_relation.delete()
            except AuthUserGroup.DoesNotExist, e:
                log.error("AuthUserGroup 关系不存在")
                log.error(repr(e))
            del_redis_token(del_user.user_token)
            del_user.delete()
        ret = {}
        ret['user_id'] = user_id
    except User.DoesNotExist:
        return JsonResponse(retcode(ret, "9999", "删除用户信息失败"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


def update_redis_token(user_token, group):
    try:
        conn = get_connection_from_pool()
        ret = conn.hset(PERMISSION_GROUP_HASH, user_token, group)
    except Exception, e:
        log.error(repr(e))
    return ret


def get_connection_from_pool():
    redis_pool = RedisTool()
    return redis_pool.get_connection()


def del_redis_token(user_token):
    try:
        conn = get_connection_from_pool()
        ret = conn.hdel(PERMISSION_GROUP_HASH, user_token)
    except Exception, e:
        log.error(repr(e))
    return ret
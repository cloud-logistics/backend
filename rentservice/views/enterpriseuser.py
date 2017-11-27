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
from django.conf import settings
from django.db.models import Q
import hashlib


log = logger.get_logger(__name__)
tz = pytz.timezone(settings.TIME_ZONE)
PERMISSION_GROUP_HASH = 'permissions_group_hash'
# PERMISSION_URL_HASH = 'permissions_url_hash'


@csrf_exempt
@api_view(['POST'])
def add_enterprise_admin(request):
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
        user_real_name = data['user_real_name']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册用户姓名不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_phone = data['user_phone']
    except Exception, e:
        user_phone = ''
        log.error(repr(e))
    try:
        user_email = data['user_email']
    except Exception, e:
        log.error(repr(e))
        user_email = ''
    try:
        avatar_url = data['avatar_url']
    except Exception, e:
        log.error(repr(e))
        avatar_url = ''
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
                    md = hashlib.md5()
                    md.update(user_password)
                    md5_pwd = md.hexdigest()
                    new_user = EnterpriseUser(user_id=uuid.uuid1(), user_name=user_name, user_password=user_password,
                                              status='', register_time=datetime.datetime.now(tz=tz),
                                              enterprise=enterprise, user_token=uuid.uuid4().hex, role=role,
                                              group=group_obj, user_alias_id=uuid.uuid1().hex, user_real_name=user_real_name,
                                              user_phone=user_phone, user_email=user_email, avatar_url=avatar_url,
                                              user_password_encrypt=md5_pwd)
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
def update_enterprise_admin(request):
    ret = {}
    data = JSONParser().parse(request)
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
        role = data['role']
    except Exception:
        return JsonResponse(retcode({}, "9999", '修改用户角色不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        group = data['group']
    except Exception:
        return JsonResponse(retcode({}, "9999", '企业用户所属群组不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        avatar_url = data['avatar_url']
    except Exception:
        return JsonResponse(retcode({}, "9999", '头像url不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        group_obj = AccessGroup.objects.get(group=group)
    except AccessGroup.DoesNotExist:
        return JsonResponse(retcode({}, "9999", '修改企业用户群组不存在'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        enterprise = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
    except EnterpriseInfo.DoesNotExist:
        return JsonResponse(retcode({}, "9999", '修改所属的企业id'), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
        user.group = group_obj
        user.enterprise_id = enterprise
        user.role = role
        user.avatar_url = avatar_url
        user.user_email = user_email
        user.user_phone = user_phone
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
def list_enterprise_user(request, group):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    group_query_set = AccessGroup.objects.all()
    group_map = {}
    for item in group_query_set:
        group_map[item.access_group_id] = item.group
    try:
        if group == 'all':
            enterprise_user_ret = EnterpriseUser.objects.all()
            page = paginator.paginate_queryset(enterprise_user_ret, request)
            enterprise_user_ser = EnterpriseUserSerializer(page, many=True)
            revised_enterprise_user_list = []
            for item in enterprise_user_ser.data:
                group_id = item['group']
                item['group'] = group_map[group_id]
                revised_enterprise_user_list.append(item)
        else:
            try:
                obj_group = AccessGroup.objects.get(group=group)
            except AccessGroup.DoesNotExist:
                return JsonResponse(retcode(errcode("9999", '企业用户群组不存在'), "9999", '企业用户群组不存在'), safe=True,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            enterprise_user_ret = EnterpriseUser.objects.filter(group=obj_group).order_by('-register_time')
            page = paginator.paginate_queryset(enterprise_user_ret, request)
            enterprise_user_ser = EnterpriseUserSerializer(page, many=True)
            revised_enterprise_user_list = []
            for item in enterprise_user_ser.data:
                group_id = item['group']
                item['group'] = group_map[group_id]
                revised_enterprise_user_list.append(item)

    except Exception, e:
        log.error(repr(e))
    return paginator.get_paginated_response(revised_enterprise_user_list)


@csrf_exempt
@api_view(['GET'])
def enterprise_user_detail(request, user_id):
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
        ser_user = EnterpriseUserSerializer(user)
        ret = ser_user.data
        ret['group'] = user.group.group
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", "查询用户信息失败"), "9999", "查询用户信息失败"), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def enterprise_user_fuzzy_query(request):
    try:
        data = JSONParser().parse(request)
        keyword = data['keyword']
    except Exception, e:
        keyword = ''
        log.error(e.message)
    user_data = EnterpriseUser.objects.filter(Q(user_name__contains=keyword) |
                                              Q(user_phone__contains=keyword)).order_by('user_name')
    fuzzy_user_list = []
    for item in user_data:
        ser_item = EnterpriseUserSerializer(item)
        ret = ser_item.data
        ret['group'] = item.group.group
        fuzzy_user_list.append(ret)
    return JsonResponse(retcode(fuzzy_user_list, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def add_enterprise_user(request):
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
                return JsonResponse(retcode({}, "0500", '登陆名已存在'), safe=True,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except EnterpriseUser.DoesNotExist:
                with transaction.atomic():
                    new_user = EnterpriseUser(user_id=uuid.uuid1(), user_name=user_name, user_password='hna12345',
                                              status='', avatar_url='', user_phone=user_phone,
                                              user_email='', register_time=datetime.datetime.now(tz=tz),
                                              enterprise=enterprise, user_token=uuid.uuid4().hex, role=role,
                                              group=group_obj, user_real_name=user_real_name, user_gender=user_gender,
                                              user_alias_id=uuid.uuid1().hex)
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
        avatar_url = data['avatar_url']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '修改头像url不能为空'), "9999", '修改头像url不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_real_name = data['user_real_name']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '修改姓名不能为空'), "9999", '修改姓名不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_gender = data['user_gender']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '修改用户性别不能为空'), "9999", '修改用户性别不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_nickname = data['user_nickname']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '修改用户性别不能为空'), "9999", '修改用户性别不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_phone = data['user_phone']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '用户号码不能为空'), "9999", '用户号码不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        enterprise_id = data['enterprise_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '企业信息id不能为空'), "9999", '企业信息id不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_id = data['user_id']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '修改用户id不能为空'), "9999", '修改用户id不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_password = data['user_password']
    except Exception:
        return JsonResponse(retcode(errcode("9999", '修改用户密码不能为空'), "9999", '修改用户密码不能为空'), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_email = data['user_email']
    except Exception, e:
        log.error(repr(e))
        user_email = ''
    try:
        user = EnterpriseUser.objects.get(user_id=user_id)
        enterprise = EnterpriseInfo.objects.get(enterprise_id=enterprise_id)
        user.user_real_name = user_real_name
        user.avatar_url = avatar_url
        user.user_phone = user_phone
        user.user_gender = user_gender
        user.user_nickname = user_nickname
        user.enterprise_id = enterprise
        user.user_email = user_email
        if user_password:
            user.user_password = user_password
            log.info("user_password is changed")
        user.save()
    except EnterpriseUser.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode(ret, "9999", '请求修改的企业用户信息不存在'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    ret={}
    ret['user_id'] = user.user_id
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def list_enterprise_user_by_enterprise_id(request, enterprise_id):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    group_query_set = AccessGroup.objects.all()
    group_map = {}
    for item in group_query_set:
        group_map[item.access_group_id] = item.group
    try:
        enterprise_user_ret = EnterpriseUser.objects.filter(enterprise_id=enterprise_id).order_by('register_time')
        page = paginator.paginate_queryset(enterprise_user_ret, request)
        enterprise_user_ser = EnterpriseUserSerializer(page, many=True)
        revised_enterprise_user_list = []
        for item in enterprise_user_ser.data:
            group_id = item['group']
            item['group'] = group_map[group_id]
            revised_enterprise_user_list.append(item)
    except Exception, e:
        log.error(repr(e))
    return paginator.get_paginated_response(revised_enterprise_user_list)


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

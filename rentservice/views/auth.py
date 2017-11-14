#! /usr/bin/env python
# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import EnterpriseUser, AuthUserGroup, AccessGroup
from rentservice.utils.retcode import *
from rest_framework.settings import api_settings
from rentservice.serializers import AccessGroupSerializer, EnterpriseUserSerializer
import uuid


log = logger.get_logger(__name__)


# @csrf_exempt
# @api_view(['POST'])
# def add_user(request):
#     ret = {}
#     data = JSONParser().parse(request)
#     try:
#         username = data['username']
#     except Exception:
#         return JsonResponse(retcode({}, "9999", '注册姓名不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         password = data['password']
#     except Exception:
#         return JsonResponse(retcode({}, "9999", '注册密码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         user = RentServiceRegUser.objects.get(user_name=username)
#         if user:
#             log.error("user exists already and return 500 error")
#             return JsonResponse(retcode({}, "0500", '用户名已存在'), safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception, e:
#         log.error(repr(e))
#     try:
#         new_user = RentServiceRegUser(reg_user_id=uuid.uuid1(), user_name=username, user_password=password,
#                                       user_token=uuid.uuid4().hex)
#         new_user.save()
#     except Exception, e:
#         log.error(repr(e))
#     ret['user_id'] = new_user.reg_user_id
#     ret['user_token'] = new_user.user_token
#     return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def auth(request):
    data = JSONParser().parse(request)
    try:
        username = data['username']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册姓名不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)
    try:
        password = data['password']
    except Exception:
        return JsonResponse(retcode({}, "9999", '注册密码不能为空'), safe=True, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = EnterpriseUser.objects.get(user_name=username, user_password=password)
    except EnterpriseUser.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "0403", '用户不存在'), safe=True, status=status.HTTP_403_FORBIDDEN)
    try:
        auth_user_group = AuthUserGroup.objects.get(user_token=user.user_token)
        access_group = AccessGroup.objects.get(access_group_id=auth_user_group.group_id)
    except AuthUserGroup.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "0403", '用户不属于任何群组'), safe=True, status=status.HTTP_403_FORBIDDEN)
    ser_user = EnterpriseUserSerializer(user)
    ret = ser_user.data
    ret['group'] = access_group.group
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def list_group(request):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    paginator = pagination_class()
    try:
        access_group_ret = AccessGroup.objects.all()
        page = paginator.paginate_queryset(access_group_ret, request)
        access_group_ser = AccessGroupSerializer(page, many=True)
    except Exception, e:
        log.error(repr(e))
    return paginator.get_paginated_response(access_group_ser.data)


@csrf_exempt
@api_view(['GET'])
def group_detail(request, access_group_id):
    try:
        group = AccessGroup.objects.get(access_group_id=access_group_id)
        ser_group = AccessGroupSerializer(group)
    except EnterpriseUser.DoesNotExist:
        return JsonResponse(retcode(errcode("9999", "查询用户信息失败"), "9999", "查询用户信息失败"), safe=True,
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(retcode(ser_group.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
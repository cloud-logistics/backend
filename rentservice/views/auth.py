#! /usr/bin/env python
# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.models import EnterpriseUser, AuthUserGroup, AccessGroup
from rentservice.utils.retcode import *
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
    except EnterpriseUser.DoesNotExist:
        log.error(repr(e))
        return JsonResponse(retcode({}, "0403", '用户不存在'), safe=True, status=status.HTTP_403_FORBIDDEN)
    try:
        auth_user_group = AuthUserGroup.objects.get(user_token=user.user_token)
        access_group = AccessGroup.objects.get(access_group_id=auth_user_group.group_id)
    except AuthUserGroup.DoesNotExist, e:
        log.error(repr(e))
        return JsonResponse(retcode({}, "0403", '用户不属于任何群组'), safe=True, status=status.HTTP_403_FORBIDDEN)
    ret = {}
    ret['user_token'] = user.user_token
    ret['group'] = access_group.group
    return JsonResponse(retcode(ret, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)

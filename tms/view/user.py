#! /usr/bin/env python
# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from tms.models import User
from tms.utils.retcode import retcode, errcode
from tms.utils.logger import get_logger
from rest_framework.settings import api_settings
from tms.serializers import UserSerializer
log = get_logger(__name__)


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

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from util import logger
from monservice.models import *
from monservice.serializers import *
from django.http import JsonResponse
from rest_framework import status
import re

log = logger.get_logger(__name__)


try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


# 运营平台拦截器
class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        if request.path.startswith(r'/container/api/v1/cloudbox/monservice') and not \
                request.path.startswith(r'/container/api/v1/cloudbox/monservice/auth'):
            try:
                token = request.META.get('HTTP_AUTHORIZATION')
                log.info("request token %s" % token)
            except Exception, e:
                log.error(e.message)
                return JsonResponse({'msg': "no authorized exception"}, safe=True,
                                    status=status.HTTP_401_UNAUTHORIZED)
            try:
                req_url = request.path
                url_set = SysAccessUrlSerializer(SysAccessUrl.objects.
                                                 filter(sys_group__user_group_fk__user_token=token), many=True).data
                flag = False
                for url in url_set:
                    result = re.match(url['access_url'], req_url)
                    if result:
                        flag = True
                        break
                if flag is False:
                    return JsonResponse({'msg': "no authorized"}, safe=True,
                                        status=status.HTTP_401_UNAUTHORIZED)
            except Exception, e:
                log.error(e.message)
                return JsonResponse({'msg': "no authorized exception"}, safe=True, status=status.HTTP_401_UNAUTHORIZED)









#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from rest_framework import status
from rentservice.utils.retcode import retcode, errcode
from rentservice.utils.redistools import RedisTool
from rentservice.models import *
from rentservice.serializers import *
from rentservice.utils import logger
import re
from django.contrib.sessions.models import Session


BIM_HASH = 'bim_hash'
PERMISSION_GROUP_HASH = 'permissions_group_hash'
PERMISSION_URL_HASH = 'permissions_url_hash'
log = logger.get_logger(__name__)

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        access_group_ret = AccessGroup.objects.all()
        access_group_list = AccessGroupSerializer(access_group_ret, many=True).data
        groupid_group_dic = {}
        for item in access_group_list:
            groupid_group_dic[item['access_group_id']] = item['group']
        ret = AuthUserGroup.objects.all()
        auth_user_group = AuthUserGroupSerializer(ret, many=True).data
        conn = self.get_connection_from_pool()
        for item in auth_user_group:
            conn.hset(PERMISSION_GROUP_HASH, item['user_token'], groupid_group_dic[item['group']])
        for item_access_group in access_group_list:
            ret = AccessUrlGroup.objects.filter(access_group__group=item_access_group['group'])
            access_url_list = []
            access_url_group = AccessUrlGroupSerializer(ret, many=True).data
            for item in access_url_group:
                access_url_list.append(item['access_url_set'])
            if access_url_list:
                final_hash_value = ','.join(access_url_list)
            else:
                final_hash_value = ''
            if final_hash_value:
                conn.hset(PERMISSION_URL_HASH, item_access_group['group'], final_hash_value)

    def process_request(self, request):
        if request.path.startswith(r'/container/api/v1/cloudbox/rentservice/'):  # 检测如果不是登录的话
            try:
                token = request.META.get('HTTP_AUTHORIZATION')
                log.info("request token %s" % token)
                conn = self.get_connection_from_pool()
                if token:
                    # try:
                    #     sess = Session.objects.get(pk=request.session.session_key)
                    #     sess_param = sess.get_decoded()
                    #     if sess_param[token] and (token in sess_param.keys()):
                    #         log.info('session is valid pass')
                    #     else:
                    #         log.info("session timeout or invalid session")
                    #         return JsonResponse(retcode(errcode("0401", "session timeout or invalid session"),
                    #                                     "0401", "session timeout or invalid session"),
                    #                             safe=True,
                    #                             status=status.HTTP_401_UNAUTHORIZED)
                    # except Session.DoesNotExist:
                    #     return JsonResponse(retcode(errcode("0401", "no authorized, session invalid"),
                    #                                 "0401", "no authorized, session invalid"),
                    #                         safe=True,
                    #                         status=status.HTTP_401_UNAUTHORIZED)
                    if conn.hexists(PERMISSION_GROUP_HASH, token):
                        group = conn.hget(PERMISSION_GROUP_HASH, token)
                        #admin level direct pass
                        if group == 'admin':
                            pass
                        #guest and operator should filter
                        else:
                            if conn.hexists(PERMISSION_URL_HASH, group):
                                url_list = conn.hget(PERMISSION_URL_HASH, group).split(',')
                                req_url = request.path
                                # print req_url
                                match_flag = False
                                for url_pattern in url_list:
                                    result = re.match(url_pattern, req_url)
                                    if result:
                                        match_flag = True
                                # 非法请求url直接返回
                                if not match_flag:
                                    return JsonResponse(retcode(errcode("0401", "no authorized"), "0401", "no authorized"), safe=True,
                                                        status=status.HTTP_401_UNAUTHORIZED)

                            else:
                                return JsonResponse(retcode(errcode("0401", "no authorized"), "0401", "no authorized"), safe=True,
                                                    status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        return JsonResponse(retcode(errcode("0401", "no authorized"), "0401", "no authorized, token is null"), safe=True,
                                            status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if request.path.startswith(r'/container/api/v1/cloudbox/rentservice/upload/'):
                        log.info("request without valid token bypass, if the request is upload api")
                    else:
                        log.info("request without valid token reject")
                        return JsonResponse(retcode(errcode("0401", "no authorized"), "0401", "令牌失效，请重新登录"), safe=True,
                                            status=status.HTTP_401_UNAUTHORIZED)
            except Exception:
                return JsonResponse(retcode(errcode("0401", "no authorized"), "0401", "no authorized exception"), safe=True,
                                    status=status.HTTP_401_UNAUTHORIZED)

    def get_connection_from_pool(self):
        redis_pool = RedisTool()
        return redis_pool.get_connection()



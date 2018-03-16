#! /usr/bin/env python
# -*- coding: utf-8 -*-
from rentservice.models import AccessGroup, AccessUrlGroup, AuthUserGroup
from rentservice.serializers import AccessGroupSerializer, AuthUserGroupSerializer, AccessUrlGroupSerializer
from rentservice.utils import logger
from rentservice.utils.redistools import RedisTool


BIM_HASH = 'bim_hash'
PERMISSION_GROUP_HASH = 'permissions_group_hash'
PERMISSION_URL_HASH = 'permissions_url_hash'
log = logger.get_logger(__name__)


def get_connection_from_pool():
    redis_pool = RedisTool()
    return redis_pool.get_connection()


def update_auth_info():
    access_group_ret = AccessGroup.objects.all()
    access_group_list = AccessGroupSerializer(access_group_ret, many=True).data
    groupid_group_dic = {}
    for item in access_group_list:
        groupid_group_dic[item['access_group_id']] = item['group']
    ret = AuthUserGroup.objects.all()
    auth_user_group = AuthUserGroupSerializer(ret, many=True).data
    conn = get_connection_from_pool()
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
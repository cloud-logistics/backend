#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from tms.view import sensor, order
from tms.view import auth

urlpatterns = [
    url(r'^receive_data$', sensor.receive_data),                           # 传感器接收数据
    url(r'^ongoing_order$', order.ongoing_order),                          # 在运订单列表
    url(r'^auth/adminauth$', auth.admin_auth),  # admn login verify
    url(r'^auth/auth$', auth.auth),  # 新增用户
    url(r'^auth/groups/detail/(?P<access_group_id>[0-9a-zA-Z-]+)$', auth.group_detail),  # 用户群组
    url(r'^auth/groups/list$', auth.list_group),  # 用户群组
    url(r'^auth/adminauthsalt$', auth.admin_auth_with_salt),  # 新增用户
    url(r'^auth/authsalt$', auth.auth_with_salt),  # user login verify
    url(r'^auth/pwdreset$', auth.change_password),  # 修改密码
    url(r'^auth/logout$', auth.auth_user_logout),  # user log out
]
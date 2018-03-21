#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from tms.view import sensor, order, flow
from tms.view import auth, user

urlpatterns = [
    url(r'^receive_data$', sensor.receive_data),                           # 传感器接收数据
    url(r'^get_order$', order.get_order),                                  # 获取订单列表
    url(r'^order_detail$', order.order_detail),                            # 获取订单详情
    url(r'^indicator_history$', order.indicator_history),                  # 获取指标曲线
    url(r'^order_statistic$', order.order_statistic),                      # 获取订单数量统计

    # url(r'^auth/auth$', auth.auth),  # 新增用户
    url(r'^auth/groups/detail/(?P<access_group_id>[0-9a-zA-Z-]+)$', auth.group_detail),  # 用户群组
    url(r'^auth/groups/list$', auth.list_group),  # 用户群组
    url(r'^auth/adminauthsalt$', auth.admin_auth_with_salt),  # 新增用户
    url(r'^auth/authsalt$', auth.auth_with_salt),  # user login verify
    url(r'^auth/pwdreset$', auth.change_password),  # 修改密码
    url(r'^auth/logout$', auth.auth_user_logout),  # user log out
    url(r'^fishing$', flow.fishing),  # 捕捞
    url(r'^loadup$', flow.load_up),  # 装车
    url(r'^loadoff$', flow.load_off),  # 装车
    url(r'^order$', flow.get_order),  # 获取订单ID
    url(r'^fisherylist$', flow.get_fishery_list),  # 获取渔场列表
    url(r'^fishtypelist$', flow.get_fishtype_list),  # 获取虾类型列表
    url(r'^unitlist$', flow.get_unit_list),  # 获取单位列表
    url(r'^user/userslist/(?P<role_id>[0-9a-zA-Z-]+)$', user.list_users),  # user log out
    url(r'^user/userdetail/(?P<user_id>[0-9a-zA-Z-]+)$', user.user_detail),  # user log out
    url(r'^user/adduser$', user.add_user),  # user log out
    url(r'^user/rmuser/(?P<user_id>[0-9a-zA-Z-]+)/$', user.del_user),  # user log out
]


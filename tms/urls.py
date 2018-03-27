#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from tms.view import sensor, order, flow
from tms.view import auth, user, notify, alarm

urlpatterns = [
    url(r'^receive_data$', sensor.receive_data),                           # 传感器接收数据
    url(r'^get_order$', order.get_order),                                  # 获取订单列表
    url(r'^order_detail$', order.order_detail),                            # 获取订单详情
    url(r'^indicator_history$', order.indicator_history),                  # 获取指标曲线
    url(r'^order_statistic$', order.order_statistic),                      # 获取订单数量统计
    url(r'^current_status$', order.current_status),                        # 获取在运虾盒指标当前值
    url(r'^history_path$', order.history_path),                            # 获取在运/已完成虾盒gps轨迹
    url(r'^threshold_list$', order.threshold_list),                        # 获取阈值列表
    url(r'^threshold$', order.add_threshold),                              # 添加阈值
    url(r'^threshold/(?P<type_id>\d+)$', order.alter_threshold),           # 修改阈值
    url(r'^threshold/(?P<type_id>\d+)', order.del_threshold),              # 删除阈值

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
    url(r'^flumelist$', flow.get_flume_list),  # 获取水箱列表
    url(r'^fishingdetail/(?P<qr_id>[0-9a-zA-Z-]+)$', flow.get_fishing_detail),  # 获取水箱列表
    url(r'^user/userslist/(?P<role_id>[0-9a-zA-Z-]+)$', user.list_users),  # user log out
    url(r'^user/userdetail/(?P<user_id>[0-9a-zA-Z-]+)$', user.user_detail),  # user log out
    url(r'^user/adduser$', user.add_user),  # user log out
    url(r'^user/rmuser/(?P<user_id>[0-9a-zA-Z-]+)/$', user.del_user),  # user log out
    url(r'^notify/list/(?P<user_id>[0-9a-zA-Z-]+)$', notify.get_notify_list_by_user),  # 获取用户所有通知
    url(r'^notify/set', notify.set_notify_read_flag),  # 更新消息状态
    url(r'^notify/delete/(?P<notify_id>[0-9]+)$', notify.delete_notify),  # 删除消息
    url(r'^alarm$', alarm.create_alarm),        # 创建告警
]


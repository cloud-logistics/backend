#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentapp import views

urlpatterns = [

    url(r'^appAuth$', views.app_auth),                             # 用户角色认证
    url(r'^nearbyContainers$', views.available_containers),        # 可用云箱列表
    url(r'^containerCategories$', views.container_types),          # 箱子种类
    url(r'^cargoCategories$', views.cargo_types),                  # 货物种类
    url(r'^saveOrder$', views.save_order),                         # 订单保存
    url(r'^myOrders$', views.my_orders),                           # 我的订单
    url(r'^orderStatus$', views.order_status),                     # 订单状态
    url(r'^orderPay$', views.order_pay),                           # 订单支付
    url(r'^getCode$', views.get_code),                             # 获取开箱码
    url(r'^statusSummary$', views.status_summary),                 # 云箱详情总汇
    url(r'^orderDetail$', views.order_detail),                     # 订单详情
    url(r'^getCarryMoney$', views.get_carry_money),                # 获取承运费用
    url(r'^getCarriageBill$', views.get_carriage_bill),            # 获取承运单

    url(r'^site$', views.add_site),                                # 新增堆场
    url(r'^site/(?P<id>\d+)/', views.delete_site),                 # 删除堆场
    url(r'^site/(?P<id>\d+)', views.modify_site),                 # 修改堆场
    url(r'^sites$', views.get_sites),                               # 获取堆场

    url(r'^siteStream/(?P<id>\d+)/', views.get_site_stream),       # 查询堆场进出箱子流水
    url(r'^boxinout$', views.box_inout),                           # 箱子进出仓库接口
    url(r'^dispatch$', views.get_dispatch),                        # 获取云箱调度策略
]

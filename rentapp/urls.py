#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentapp import views

urlpatterns = [

    url(r'^nearbyContainers$', views.available_containers),        # 可用云箱列表
    url(r'^containerCategories$', views.container_types),          # 箱子种类
    url(r'^cargoCategories$', views.cargo_types),                  # 货物种类
    url(r'^saveOrder$', views.save_order),                         # 订单保存
    url(r'^myOrders$', views.my_orders),                           # 我的订单
    url(r'^orderStatus$', views.order_status),                     # 订单状态
    url(r'^orderPay$', views.order_pay),                           # 订单支付

]

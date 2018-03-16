#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from tms.view import flow


urlpatterns = [

    url(r'^fishing$', flow.fishing),                                                # 捕捞
    url(r'^loadup$', flow.load_up),                                                    # 装车
    url(r'^loadoff/(?P<user_id>[0-9a-zA-Z-]+)$', flow.load_off),                      # 装车

    url(r'^order$', flow.get_order),                     # 获取订单ID
    url(r'^fisherylist$', flow.get_fishery_list),        # 获取渔场列表
    url(r'^fishtypelist$', flow.get_fishtype_list),      # 获取虾类型列表
    url(r'^unitlist$', flow.get_unit_list),          # 获取单位列表

]



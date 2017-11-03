#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentapp import views

urlpatterns = [
    url(r'^site$', views.add_site),                                # 新增堆场
    url(r'^site/(?P<id>\d+)/', views.delete_site),                 # 删除堆场
    url(r'^site/(?P<id>\d+)', views.modify_site),                  # 修改堆场
    url(r'^sites$', views.get_sites),                              # 获取堆场

    url(r'^siteStream/(?P<id>\d+)/', views.get_site_stream),       # 查询堆场进出箱子流水
    url(r'^boxinout$', views.box_inout),                           # 箱子进出仓库接口


]

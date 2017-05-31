#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from monservice import views

urlpatterns = [
    url(r'^auth$', obtain_jwt_token),
    url(r'^containers$', views.containers_overview),
    url(r'^satellites$', views.satellites_overview),
    url(r'^realtimeInfo$', views.realtime_message),               # 实时报文
    url(r'^containerInstantInfo$', views.realtime_position),      # 实时位置
    url(r'^containerhistory$', views.history_path),               # 历史轨迹
    url(r'^alerts$', views.alarm_monitor),                        # 报警监控
    url(r'^options$', views.options_to_show),                     # 报警监控
    url(r'^basicInfo$', views.basic_info),                        # 基础信息查询
    url(r'^historyMsg$', views.history_message),                  # 历史报文
    url(r'^statusSummary$', views.status_summary),                # 云箱状态汇总
]

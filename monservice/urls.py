#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from monservice import views

urlpatterns = [
    # url(r'^auth$', obtain_jwt_token),
    url(r'^auth$', views.verify_user),
    url(r'^containers$', views.containers_overview),
    url(r'^satellites$', views.satellites_overview),
    url(r'^realtimeInfo$', views.realtime_message),               # 实时报文
    url(r'^containerInstantInfo$', views.realtime_position),      # 实时位置
    url(r'^containerhistory$', views.history_path),               # 历史轨迹
    url(r'^alerts$', views.alarm_monitor),                        # 报警监控
    url(r'^options$', views.options_to_show),                     # 报警监控
    url(r'^basicInfo$', views.basic_info),                        # 基础信息查询
    url(r'^containerReportHistory$', views.history_message),      # 历史报文
    url(r'^securityConfig$', views.security_config),              # 云箱安全参数设置
    url(r'^basicInfoManage$', views.basic_info_manage),           # 基础信息管理
    url(r'^basicInfoConfig$', views.basic_info_config),           # 云箱基础信息录入
    url(r'^mycontainers$', views.mycontainers),                   # 承运方页面
    url(r'^containersonlease$', views.containers_on_release),     # 承运方在租页面
    url(r'^availablecontainers$', views.containers_available),    # 承运方可用云箱
    url(r'^command$', views.send_command),                        # 向终端发送command
    url(r'^containerHistoryStatus$', views.indicator_history),    # 实时报文指标历史曲线
    url(r'^analysisresult$', views.analysis_result),              # 分析报告
    url(r'^boxStatus$', views.status_summary),                    # 云箱状态汇总
    url(r'^operationoverview$', views.operation_overview),            # 运营状态概览
]

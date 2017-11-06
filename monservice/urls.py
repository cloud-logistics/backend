#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from monservice import views
from monservice.view import site
from monservice.view import dispatch

urlpatterns = [
    url(r'^auth$', views.verify_user),
    url(r'^containers$', views.containers_overview),              # 云箱概览
    url(r'^realtimeInfo$', views.realtime_message),               # 实时状态
    url(r'^containerInstantInfo$', views.realtime_position),      # 实时位置
    url(r'^containerhistory$', views.history_path),               # 历史轨迹
    url(r'^alerts$', views.alarm_monitor),                        # 报警监控
    url(r'^options$', views.options_to_show),                     # 报警监控
    url(r'^basicInfo$', views.basic_info),                        # 基础信息查询
    url(r'^containerReportHistory$', views.history_message),      # 历史报文
    url(r'^securityConfig$', views.security_config),              # 云箱安全参数设置
    url(r'^basicInfoManage$', views.basic_info_manage),           # 基础信息管理
    url(r'^basicInfoConfig$', views.basic_info_config),           # 云箱基础信息录入
    url(r'^basicInfo/(?P<id>\w+)/', views.remove_basic_info),     # 云箱基础信息删除
    url(r'^basicInfoMod$', views.modify_basic_info),              # 云箱基础信息修改
    url(r'^mycontainers$', views.mycontainers),                   # 承运方页面
    url(r'^containersonlease$', views.containers_on_release),     # 承运方在租页面
    url(r'^availablecontainers$', views.containers_available),    # 承运方可用云箱
    url(r'^command$', views.send_command),                        # 向终端发送command
    url(r'^containerHistoryStatus$', views.indicator_history),    # 实时报文指标历史曲线
    url(r'^analysisresult$', views.analysis_result),              # 分析报告
    url(r'^boxStatus$', views.status_summary),                    # 云箱状态汇总
    url(r'^operationoverview$', views.operation_overview),        # 运营状态概览
    url(r'^requestlease$', views.rent),                           # 我要租赁
    url(r'^returncontainer$', views.return_container),            # 归还云箱
    url(r'^getSecurityConfig$', views.get_security_config),       # 获取运行安全参数

    url(r'^sites$', site.add_site),                              # 增加堆场
    url(r'^sites/(?P<id>\d+)$', site.delete_site),               # 删除堆场
    url(r'^sites/(?P<id>\d+)', site.modify_site),                # 修改堆场
    url(r'^allsites$', site.get_sites),                          # 查询堆场
    url(r'^boxbysite/(?P<id>\d+)', site.get_site_boxes),         # 查询堆场箱子
    url(r'^dispatch$', dispatch.get_dispatches),                  # 获取调度
    url(r'^dispatch/', dispatch.create_dispatches),               # 加入调度
    url(r'^distribution$', site.get_box_by_allsite),          # 获取热力图数据

    url(r'^nationlist$', views.get_nation_list),                          # 获取国家列表
    url(r'^provincelist/(?P<nation_id>\d+)$', views.get_province_list),   # 根据国家获取省列表
    url(r'^citylist/(?P<province_id>\d+)$', views.get_city_list),         # 根据省获取城市列表
    url(r'^getlnglat$', views.get_lnglat),                        # 根据省获取城市列表
    url(r'^getPosition$', views.get_position),                    # 根据经纬度获取地名

]

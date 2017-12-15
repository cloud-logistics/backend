#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from monservice import views
from monservice.view import site, dispatch, maintenance

urlpatterns = [
    url(r'^auth$', views.login),                                  # 登录认证
    url(r'^logout$', views.logout),                               # 用户退出
    url(r'^message$', views.get_message),                         # 消息查看
    url(r'^containers$', views.containers_overview),              # 云箱概览
    url(r'^realtimeInfo$', views.realtime_message),               # 实时状态
    url(r'^containerInstantInfo$', views.realtime_position),      # 实时位置
    url(r'^containerhistory$', views.history_path),               # 历史轨迹
    url(r'^historypath/$', views.box_history_path),               # 云箱历史轨迹
    url(r'^alerts$', views.alarm_monitor),                        # 报警监控
    url(r'^options$', views.options_to_show),                     # 选项查询
    url(r'^basicInfo$', views.basic_info),                        # 基础信息查询
    url(r'^securityConfig$', views.security_config),              # 云箱安全参数设置
    url(r'^basicInfoConfig$', views.basic_info_config),           # 云箱基础信息录入
    url(r'^basicInfo/(?P<id>\w+)/', views.remove_basic_info),     # 云箱基础信息删除
    url(r'^basicInfoMod$', views.modify_basic_info),              # 云箱基础信息修改
    url(r'^getContainerID/(?P<rfid>\w+)/', views.get_containerid_by_rfid),  # 根据云箱RFID查询云箱ID
    url(r'^command$', views.send_command),                        # 向终端发送command
    url(r'^containerHistoryStatus$', views.indicator_history),    # 实时报文指标历史曲线
    url(r'^rentContainerHistory$', views.rent_container_history), # 租赁平台调用历史曲线
    url(r'^rentRealTimeMsg$', views.rent_real_time_msg),          # 租赁平台调用实时报文
    url(r'^boxStatus$', views.status_summary),                    # 云箱状态汇总
    url(r'^operationoverview$', views.operation_overview),        # 运营状态概览
    url(r'^getSecurityConfig$', views.get_security_config),       # 获取运行安全参数

    url(r'^sites$', site.add_site),                               # 增加堆场
    url(r'^sites/(?P<id>\d+)$', site.delete_site),                # 删除堆场
    url(r'^sites/(?P<id>\d+)', site.modify_site),                 # 修改堆场
    url(r'^allsites$', site.get_sites),                           # 查询堆场
    url(r'^boxbysite/(?P<id>\d+)', site.get_site_boxes),          # 查询堆场箱子
    url(r'^dispatch$', dispatch.get_dispatches),                  # 获取调度
    url(r'^typedispatch$', dispatch.get_type_dispatches),         # 获取按类型调度
    url(r'^disHistory$', dispatch.get_dispatches_history),        # 获取调度历史
    url(r'^dispatch/', dispatch.create_dispatches),               # 加入调度
    url(r'^actdispatch$', dispatch.act_dispatches),               # 模拟调度过程
    url(r'^distribution$', site.get_box_by_allsite),              # 获取热力图数据
    url(r'^siteStream/(?P<id>\d+)/', site.get_site_stream),       # 查询堆场进出箱子流水
    url(r'^boxinout$', site.box_inout),                           # 箱子进出仓库接口
    url(r'^checknum$', site.check_all_num),                       # 测试检查仓库箱子可用数

    url(r'^querydispatch/(?P<site_id>\d+)/', dispatch.get_dispatch_by_site),      # 根据堆场查询调度信息
    url(r'^dispatchout$', site.dispatchout),                      # 调度出仓接口
    url(r'^dispatchin$', site.dispatchin),                        # 调度入仓接口

    url(r'^nationlist$', views.get_nation_list),                          # 获取国家列表
    url(r'^provincelist/(?P<nation_id>\d+)$', views.get_province_list),   # 根据国家获取省列表
    url(r'^citylist/(?P<province_id>\d+)$', views.get_city_list),         # 根据省获取城市列表
    url(r'^getlnglat$', views.get_lnglat),                        # 根据省获取城市列表
    url(r'^getPosition$', views.get_position),                    # 根据经纬度获取地名

    url(r'^safeSettings$', views.get_all_safe_settings),                  # 查询所有类型箱子安全参数
    url(r'^safeSettings/(?P<type_id>\d+)$', views.get_safe_settings),     # 查询箱子安全参数
    url(r'^safeSettings/(?P<type_id>\d+)', views.save_safe_settings),     # 修改箱子安全参数

    url(r'^maintenance$', maintenance.create_maintenance),                               # 增加维修点
    url(r'^maintenance/(?P<maintenance_id>\d+)$', maintenance.delete_maintenance),       # 删除维修点
    url(r'^maintenance/(?P<maintenance_id>\d+)', maintenance.update_maintenance),        # 修改维修点
    url(r'^allmaintenance$', maintenance.get_maintenance),                               # 查询维修点

    url(r'^getHuarenData$', views.get_huaren_data),               # 华人医药查询接口



]

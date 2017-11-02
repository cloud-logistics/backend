#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentservice.views import enterprise
from rentservice.views import site
from rentservice.views import auth
from rentservice.views import enterpriseuser
from rentservice.views import boxtype
from rentservice.views import regions
from rentservice.views import boxrentservice
from rentservice.views import appointment

urlpatterns = [
    url(r'^rentservice/enterprise/enterpriseinfo/addenterpriseinfo/$', enterprise.add_enterprise_info),  # 企业信息增加接口
    url(r'^rentservice/enterprise/enterpriseinfo/updateenterpriseinfo/$', enterprise.update_enterprise_info),  # 企业信息更新接口
    url(r'^rentservice/enterprise/enterpriseinfo/(?P<enterprise_id>[0-9a-zA-Z-]+)/$', enterprise.del_enterpise_info),
    url(r'^rentservice/enterprise/enterpriseinfo/list$', enterprise.list_enterpise_info),
    url(r'^rentservice/enterprise/enterpriseinfo/detail/(?P<enterprise_id>[0-9a-zA-Z-]+)/$', enterprise.enterpise_info_detail),
    url(r'^rentservice/enterprise/enterpriseinfo/depositconfirm/$', enterprise.enterpise_deposit_confirm),
    # 企业信息更新接口
    url(r'^rentservice/site/list/(?P<latitude>[0-9.]+)/(?P<longitude>[0-9.]+)$', site.get_site_list),
    # 获取堆场列表
    # url(r'^auth/adduser$', auth.add_user),  # 新增用户
    url(r'^auth/auth$', auth.auth),  # 新增用户
    url(r'^rentservice/site/list/province/(?P<province>[0-9]+)/city/(?P<city>[0-9]+)$', site.get_site_by_province),
    # 获取堆场列表
    url(r'^rentservice/site/detail/(?P<site_id>[0-9a-zA-Z-]+)$', site.get_site_detail),  # 获取堆场详情
    url(r'^rentservice/boxtype/list', boxtype.get_box_type_list),  # 获取箱子类型
    url(r'^rentservice/enterpriseuser/addenterpriseuser/$', enterpriseuser.add_enterprise_user),  # 用户信息添加
    url(r'^rentservice/enterpriseuser/updateenterpriseuser/$', enterpriseuser.update_enterprise_user),  # 用户信息修改
    url(r'^rentservice/enterpriseuser/(?P<user_id>[0-9a-zA-Z-]+)/$', enterpriseuser.del_enterprise_user),  # 删除用户
    url(r'^rentservice/enterpriseuser/list$', enterpriseuser.list_enterprise_user),  # 用户列表
    url(r'^rentservice/enterpriseuser/detail/(?P<user_id>[0-9a-zA-Z-]+)/$', enterpriseuser.enterprise_user_detail),  # 用户详情
    url(r'^rentservice/regions/provinces', regions.get_province_list),  # 获取省列表
    url(r'^rentservice/regions/cities/(?P<province_id>[0-9]+)$', regions.get_city_list),  # 获取制定省的市列表
    url(r'^rentservice/boxrentservice/order$', boxrentservice.rent_boxes_order),  # 租箱
    url(r'^rentservice/appointment/create', appointment.create_appointment),  # 承租方预约
    url(r'^rentservice/appointment/(?P<user_id>[0-9a-zA-Z-]+)/list$', appointment.get_list_by_user),  # 承租方预约列表查询
    url(r'^rentservice/appointment/(?P<appointment_id>[0-9a-zA-Z-]+)/detail$', appointment.get_appointment_detail),  # 预约详情查询

]

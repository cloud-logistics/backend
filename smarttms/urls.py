#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from smarttms.views import operator, auth, enterprise, enterpriseuser

urlpatterns = [
    url(r'^auth/authsalt$', auth.auth_with_salt),  # user login verify
    url(r'^auth/pwdreset$', auth.change_password),  # 修改密码
    url(r'^auth/logout$', auth.auth_user_logout),  # user log out
    url(r'^enterpriseinfo/addenterpriseinfo/$', enterprise.add_enterprise_info),
    url(r'^enterpriseinfo/updateenterpriseinfo/$', enterprise.update_enterprise_info),
    # 企业信息更新接口
    url(r'^enterpriseinfo/(?P<enterprise_id>[0-9a-zA-Z-]+)/$', enterprise.del_enterpise_info),
    url(r'^enterpriseinfo/list$', enterprise.list_enterpise_info),
    url(r'^enterpriseinfo/detail/(?P<enterprise_id>[0-9a-zA-Z-]+)/$',
        enterprise.enterpise_info_detail),
    url(r'^enterpriseinfo/depositconfirm$', enterprise.enterpise_deposit_confirm),
    url(r'^enterpriseinfo/fuzzy$', enterprise.enterprise_fuzzy_query),
    url(r'^enterpriseinfo/userfuzzy$', enterprise.enterpriseuser_fuzzy_query),

    url(r'^enterpriseuser/adduser/$', enterpriseuser.add_enterprise_user),  # 添加普通用户
    url(r'^enterpriseuser/updateuser/$', enterpriseuser.update_enterprise_user),  # 普通用户修改
    url(r'^enterpriseuser/(?P<user_id>[0-9a-zA-Z-]+)/$', enterpriseuser.del_enterprise_user),  # 删除用户
    url(r'^enterpriseuser/list/(?P<group>[a-z]+)$', enterpriseuser.list_enterprise_user),  # 用户列表
    url(r'^enterpriseuser/list/enterprise/(?P<enterprise_id>[0-9a-zA-Z-]+)$',
        enterpriseuser.list_enterprise_user_by_enterprise_id),  # 用户列表
    url(r'^enterpriseuser/detail/(?P<user_id>[0-9a-zA-Z-]+)/$', enterpriseuser.enterprise_user_detail),
    url(r'^enterpriseuser/fuzzy$', enterpriseuser.enterprise_user_fuzzy_query),

    url(r'^operator/home_page$', operator.home_page),                  # 运营方首页数据
    url(r'^operator/box_status$', operator.box_status),                # 运营方云箱状态
    url(r'^operator/box_detail$', operator.box_detail),                # 获取箱子类型

]


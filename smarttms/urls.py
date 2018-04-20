#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from smarttms.views import operator, auth, enterprise

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
    url(r'^operator/home_page$', operator.home_page),                  # 运营方首页数据
]


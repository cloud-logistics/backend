#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentservice.views import enterprise
from rentservice.views import site
from rentservice.views import auth

urlpatterns = [
    url(r'^rentservice/enterprise/enterpriseinfo/addenterpriseinfo$', enterprise.add_enterprise_info),  # 企业信息增加接口
    url(r'^rentservice/enterprise/enterpriseinfo/updateenterpriseinfo$', enterprise.update_enterprise_info),  # 企业信息更新接口
    url(r'^rentservice/enterprise/enterpriseinfo/(?P<enterprise_id>[0-9a-zA-Z-]+)$', enterprise.del_enterpise_info),
    # 企业信息更新接口
    url(r'^rentservice/site/list/(?P<latitude>[0-9.]+)/(?P<longitude>[0-9.]+)$', site.get_site_list),
    # 获取堆场列表
    url(r'^auth/adduser$', auth.add_user),  #新增用户
    url(r'^auth/auth$', auth.auth),  #新增用户
]

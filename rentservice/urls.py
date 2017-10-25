#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentservice.views import enterprise

urlpatterns = [
    url(r'^rentservice/enterprise/enterpriseinfo/addenterpriseinfo$', enterprise.add_enterprise_info),  #企业信息增加接口
    url(r'^rentservice/enterprise/enterpriseinfo/updateenterpriseinfo$', enterprise.update_enterprise_info),  #企业信息更新接口
    url(r'^rentservice/enterprise/enterpriseinfo/(?P<enterprise_id>[0-9a-zA-Z-]+)$', enterprise.del_enterpise_info),  #企业信息更新接口
]

#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from smarttms.views import operator

urlpatterns = [
    url(r'^operator_home_page$', operator.home_page),                  # 运营方首页数据

]


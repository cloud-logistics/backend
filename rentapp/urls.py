#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentapp import views

urlpatterns = [

    url(r'^nearbyContainers$', views.available_containers),        # 可用云箱列表

]

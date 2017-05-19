#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from sensor import views

urlpatterns = [
    url(r'^sensor$', views.input_data),
]
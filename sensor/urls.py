#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from sensor import views

urlpatterns = [
    url(r'^sensor$', views.input_data),
    url(r'^handset/nextsite$', views.nextsite),
    url(r'^precintl/savedata$', views.save_precintl_data),
    url(r'^getdata$', views.get_data),
    url(r'^dumpdata$', views.dump_data),

]
# -*- coding: utf-8 -*-


from django.conf.urls import url
from tms.view import sensor, order

urlpatterns = [
    url(r'^receive_data$', sensor.receive_data),                           # 传感器接收数据
    url(r'^ongoing_order$', order.ongoing_order),                          # 在运订单列表


]
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from smarttms.views import operator, auth, enterprise, enterpriseuser, shipper, sensor, driver

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
    url(r'^operator/box_rent$', operator.box_rent),                    # 扫码用箱
    url(r'^operator/box_order_history$', operator.box_order_history),  # 箱单记录

    url(r'^driver/query/(?P<deviceid>[0-9a-zA-Z-]+)/$', driver.order_info),  # 司机扫描查询接口
    url(r'^driver/ack/order/$', driver.ack_order),                       # 司机确认提货

    # 司机接口
    url(r'^driver/query/(?P<deviceid>[0-9a-zA-Z-]+)/$', driver.order_info),  # 司机扫描查询接口
    url(r'^driver/ack/order/$', driver.ack_order),                       # 司机确认提货
    url(r'^driver/orders/(?P<shop_id>[0-9]+)/$', driver.order_list),                       # 司机确认提货


    url(r'^receive_data$', sensor.receive_data),                           # 传感器接收数据

    # 发货方接口
    url(r'^shipper/boxlist$', shipper.get_box_list),        # 发货方首页云箱列表
    url(r'^shipper/shoplist$', shipper.get_shop_list),      # 门店列表
    url(r'^shipper/goodslist$', shipper.get_goods_list),    # 货物列表
    url(r'^shipper/boxdetail$', shipper.get_box_detail),    # 云箱详情
    url(r'^shipper/goodsorder$', shipper.create_goodsorder),  # 创建运单
    url(r'^shipper/orderlist$', shipper.get_order_list),       # 获取运单列表
    url(r'^shipper/goodsorder/(?P<order_id>[0-9a-zA-Z-]+)$', shipper.update_goods_order),  # 修改运单
    url(r'^shipper/goodsorder/(?P<order_id>[0-9a-zA-Z-]+)', shipper.delete_goods_order),  # 删除运单
    url(r'^shipper/allgoodsorder', shipper.get_transporting_goods_orders),   # 获取所有运单列表
    url(r'^shipper/orders_by_day$', shipper.get_orders_by_day),   # 按天查询所有运单列表
    url(r'^shipper/goodsorder/(?P<order_id>[0-9a-zA-Z-]+)$', shipper.get_goods_order),  # 获取运单详情
]


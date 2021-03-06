#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from rentservice.views import enterprise
from rentservice.views import site
from rentservice.views import auth
from rentservice.views import enterpriseuser
from rentservice.views import boxtype
from rentservice.views import regions
from rentservice.views import boxrentservice
from rentservice.views import appointment
from rentservice.views import userinfo
from rentservice.views import upload
from rentservice.views import entleaseinfo
from rentservice.views import boxinfo
from rentservice.views import boxbill
from rentservice.views import notify
from rentservice.views import dashboard
from rentservice.views import param
from rentservice.views import crypt

urlpatterns = [
    url(r'^rentservice/enterprise/enterpriseinfo/addenterpriseinfo/$', enterprise.add_enterprise_info),  # 企业信息增加接口
    url(r'^rentservice/enterprise/enterpriseinfo/updateenterpriseinfo/$', enterprise.update_enterprise_info),
    # 企业信息更新接口
    url(r'^rentservice/enterprise/enterpriseinfo/(?P<enterprise_id>[0-9a-zA-Z-]+)/$', enterprise.del_enterpise_info),
    url(r'^rentservice/enterprise/enterpriseinfo/list$', enterprise.list_enterpise_info),
    url(r'^rentservice/enterprise/enterpriseinfo/detail/(?P<enterprise_id>[0-9a-zA-Z-]+)/$',
        enterprise.enterpise_info_detail),
    url(r'^rentservice/enterprise/enterpriseinfo/depositconfirm$', enterprise.enterpise_deposit_confirm),
    url(r'^rentservice/enterprise/enterpriseinfo/fuzzy$', enterprise.enterprise_fuzzy_query),
    url(r'^rentservice/enterprise/enterpriseinfo/userfuzzy$', enterprise.enterpriseuser_fuzzy_query),
    # 企业信息更新接口
    url(r'^rentservice/site/list/(?P<latitude>[0-9.]+)/(?P<longitude>[0-9.]+)$', site.get_site_list),
    # 获取堆场列表
    url(r'^auth/adminauth$', auth.admin_auth),  # admn login verify
    url(r'^auth/auth$', auth.auth),  # 新增用户
    url(r'^auth/groups/detail/(?P<access_group_id>[0-9a-zA-Z-]+)$', auth.group_detail),  # 用户群组
    url(r'^auth/groups/list$', auth.list_group),  # 用户群组
    url(r'^auth/adminauthsalt$', auth.admin_auth_with_salt),  # 新增用户
    url(r'^auth/authsalt$', auth.auth_with_salt),  # user login verify
    url(r'^auth/pwdreset$', auth.change_password),  # 修改密码
    url(r'^auth/logout$', auth.auth_user_logout),  # user log out
    url(r'^rentservice/site/list/province/(?P<province>[0-9]+)/city/(?P<city>[0-9]+)$', site.get_site_by_province),
    # 获取堆场列表
    url(r'^rentservice/site/detail/(?P<site_id>[0-9a-zA-Z-]+)$', site.get_site_detail),  # 获取堆场详情
    url(r'^rentservice/boxtype/list', boxtype.get_box_type_list),  # 获取箱子类型
    url(r'^rentservice/enterpriseuser/addenterpriseuser/$', enterpriseuser.add_enterprise_admin),  # 添加管理员用户
    url(r'^rentservice/enterpriseuser/updateenterpriseuser/$', enterpriseuser.update_enterprise_admin),  # 修改管理员用户
    url(r'^rentservice/enterpriseuser/adduser/$', enterpriseuser.add_enterprise_user),  # 添加普通用户
    url(r'^rentservice/enterpriseuser/updateuser/$', enterpriseuser.update_enterprise_user),  # 普通用户修改
    url(r'^rentservice/enterpriseuser/(?P<user_id>[0-9a-zA-Z-]+)/$', enterpriseuser.del_enterprise_user),  # 删除用户
    url(r'^rentservice/enterpriseuser/list/(?P<group>[a-z]+)$', enterpriseuser.list_enterprise_user),  # 用户列表
    url(r'^rentservice/enterpriseuser/list/enterprise/(?P<enterprise_id>[0-9a-zA-Z-]+)$',
        enterpriseuser.list_enterprise_user_by_enterprise_id),  # 用户列表
    url(r'^rentservice/enterpriseuser/detail/(?P<user_id>[0-9a-zA-Z-]+)/$', enterpriseuser.enterprise_user_detail),
    url(r'^rentservice/enterpriseuser/fuzzy$', enterpriseuser.enterprise_user_fuzzy_query),
    # 用户详情
    url(r'^rentservice/regions/provinces', regions.get_province_list),  # 获取省列表
    url(r'^rentservice/regions/cities/(?P<province_id>[0-9]+)$', regions.get_city_list),  # 获取制定省的市列表
    url(r'^rentservice/appointment/create', appointment.create_appointment),  # 承租方预约
    url(r'^rentservice/appointment/(?P<user_id>[0-9a-zA-Z-]+)/list$', appointment.get_list_by_user),  # 承租方预约列表查询
    url(r'^rentservice/appointment/(?P<appointment_code>[0-9a-zA-Z-]+)/detail$', appointment.get_appointment_detail),
    # 预约详情查询
    url(r'^rentservice/userinfo/list/(?P<user_id>[0-9a-zA-Z-]+)/process', userinfo.get_process_order_list),
    # 承运人的在运箱子查询
    url(r'^rentservice/userinfo/list/(?P<user_id>[0-9a-zA-Z-]+)/finished', userinfo.get_finished_order_list),
    # 预约详情查询
    url(r'^rentservice/upload/(?P<filename>[^/]+)$', upload.FileUploadView.as_view()),  # 新增上传接口
    # 承运人的历史箱子查询
    url(r'^rentservice/enterlease/list/(?P<enterprise_id>[0-9a-zA-Z-]+)/process',
        entleaseinfo.get_enterprise_lease_process_list),
    # 承运人的在运箱子查询
    url(r'^rentservice/enterlease/list/(?P<enterprise_id>[0-9a-zA-Z-]+)/finished',
        entleaseinfo.get_enterprise_lease_finish_list),
    # 承运人的历史箱子查询
    url(r'^rentservice/boxrentservice/createorder$', boxrentservice.rent_boxes_order),  # 租箱
    url(r'^rentservice/boxrentservice/finishorder$', boxrentservice.finish_boxes_order),  # 还箱
    url(r'^rentservice/boxrentservice/boxtypefee$', boxrentservice.set_rent_fee_rate),  # 设置每小时费用
    url(r'^rentservice/boxrentservice/boxtypeinfo$', boxrentservice.box_type_info_list),  # 云箱类型信息列表
    url(r'^rentservice/userinfo/(?P<user_id>[0-9a-zA-Z-]+)/dash$', userinfo.get_dash_data),  # app获取dash信息
    url(r'^rentservice/appointment/cancel', appointment.cancel_appointment),  # 取消预约
    url(r'^rentservice/boxinfo/query', boxinfo.get_box_info_list),  # 查询箱子list
    url(r'^rentservice/site/stat/(?P<site_id>[0-9a-zA-Z-]+)$', site.get_site_stat),  # 查询仓库的统计信息
    url(r'^rentservice/site/nearby/(?P<latitude>[0-9.]+)/(?P<longitude>[0-9.]+)$', site.get_site_list_nearby),
    # 获取附近20公里的仓库
    url(r'^rentservice/boxinfo/detail/(?P<box_id>[0-9a-zA-Z-]+)$', boxinfo.get_box_detail),  # 查询箱子详情
    url(r'^rentservice/appointment/(?P<user_id>[0-9a-zA-Z-]+)/processlist$', appointment.get_user_process_list),
    # 承运方进行中的预约单
    url(r'^rentservice/appointment/(?P<user_id>[0-9a-zA-Z-]+)/finishedlist$', appointment.get_user_finished_list),
    # 承运方已完成的预约单
    url(r'^rentservice/boxinfo/stat/(?P<box_id>[0-9a-zA-Z-]+)$', boxinfo.get_box_stat),  # 查询箱子统计
    url(r'^rentservice/boxinfo/leaselist/(?P<box_id>[0-9a-zA-Z-]+)$', boxinfo.get_box_lease_list),  # 查询箱子租赁记录
    url(r'^rentservice/boxbill/realtimebill', boxbill.box_bill_real_time_all),  # 所有企业计费情况报表
    url(r'^rentservice/boxbill/monthbill/(?P<enterprise_id>[0-9a-zA-Z-]+)$', boxbill.enterprise_month_bill),
    # 所有企业计费情况报表
    url(r'^rentservice/boxbill/detail/(?P<enterprise_id>[0-9a-zA-Z-]+)/(?P<date>[0-9-]+)$',
        boxbill.enterprise_month_bill_detail),  # 所有企业计费情况报表
    url(r'^rentservice/boxbill/filtertotalbill', boxbill.box_bill_real_time_all_filter),  # 所有企业计费情况报表
    url(r'^rentservice/notify/list/(?P<user_id>[0-9a-zA-Z-]+)$',
        notify.get_notify_list_by_user),  # 获取用户所有通知
    url(r'^rentservice/notify/set',
        notify.set_notify_read_flag),  # 更新消息状态
    url(r'^rentservice/notify/delete/(?P<notify_id>[0-9]+)$',
        notify.delete_notify),  # 删除消息
    url(r'^rentservice/appointment/(?P<appointment_id>[0-9a-zA-Z-]+)/detailbyid$',
        appointment.get_appointment_detail_by_id),
    # 预约详情查询
    url(r'^rentservice/appointment/(?P<appointment_code>[0-9a-zA-Z-]+)/detail/(?P<site_id>[0-9]+)$',
        appointment.get_appointment_detail_by_site),
    # 预约详情查询
    url(r'^rentservice/site/all$', site.get_all_site),
    # 获取所有的site
    url(r'^rentservice/site/filter$', site.get_site_by_filter),
    # 有条件获取sitelist
    url(r'^rentservice/dashboard/info$', dashboard.get_dash_data),
    # 获取dashboard的信息
    url(r'^rentservice/param/set$', param.set_param),
    url(r'^rentservice/param/all$', param.get_all_params),
    url(r'^param/get/(?P<param_key>[0-9a-zA-Z_-]+)$', param.get_param),
    url(r'^rentservice/appointment/enterpriselist$', appointment.get_enterprise_appointment),
    url(r'^rentservice/appointment/enterprise/(?P<appointment_id>[0-9a-zA-Z-]+)/detail$',
        appointment.get_enterprise_appointment_detail),
    url(r'^rentservice/blecrypt/enc$', crypt.ble_encrypt),
    url(r'^rentservice/blecrypt/dec', crypt.ble_decrypt),
]

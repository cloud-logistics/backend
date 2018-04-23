# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
import datetime
import pytz


timezone = pytz.timezone('Asia/Shanghai')


class AccessGroup(models.Model):
    access_group_id = models.CharField(max_length=48, primary_key=True)
    group = models.CharField(max_length=32)


class AuthUserGroup(models.Model):
    auth_id = models.CharField(max_length=48, primary_key=True)
    user_token = models.CharField(max_length=64)
    group = models.ForeignKey(AccessGroup, related_name='auth_user_group_fk')


class AccessUrlGroup(models.Model):
    access_url_id = models.CharField(max_length=48, primary_key=True)
    access_url_set = models.CharField(max_length=128)
    access_group = models.ForeignKey(AccessGroup, related_name='access_url_group_fk')


class EnterpriseInfo(models.Model):
    enterprise_id = models.CharField(max_length=48, primary_key=True)
    enterprise_name = models.CharField(max_length=128)
    enterprise_tele = models.CharField(max_length=32)
    enterprise_license_id = models.CharField(max_length=32)
    enterprise_license_id_url = models.CharField(max_length=256)
    enterprise_legal_rep_name = models.CharField(max_length=128)
    enterprise_email = models.CharField(max_length=128)
    enterprise_deposit = models.BigIntegerField(default=0)
    enterprise_deposit_status = models.IntegerField(default=0)
    enterprise_address = models.CharField(max_length=128, default='')
    enterprise_homepage_url = models.CharField(max_length=128, default='')
    register_time = models.DateTimeField(default=datetime.datetime.today())
    last_update_time = models.DateTimeField(default=datetime.datetime.today())


class EnterpriseUser(models.Model):
    user_id = models.CharField(max_length=48, primary_key=True)
    user_name = models.CharField(max_length=48)
    user_password = models.CharField(max_length=32)
    register_time = models.DateTimeField(default=datetime.datetime.today())
    status = models.CharField(max_length=16)
    avatar_url = models.CharField(max_length=256)
    user_phone = models.CharField(max_length=16)
    user_email = models.CharField(max_length=128)
    enterprise = models.ForeignKey(EnterpriseInfo, related_name='enterprise_user_enterprise_info_fk', null=True)
    user_token = models.CharField(max_length=64, default='')
    role = models.CharField(max_length=16, default='user')
    role_type = models.IntegerField(default=0) #
    group = models.ForeignKey(AccessGroup, null=True)
    user_real_name = models.CharField(max_length=48, default='')
    user_gender = models.CharField(max_length=8, default='')
    user_nickname = models.CharField(max_length=48, default='')
    user_alias_id = models.CharField(max_length=64, default='')
    user_password_encrypt = models.CharField(max_length=256, default='')


class UserAppointment(models.Model):
    appointment_id = models.CharField(max_length=48, primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser, related_name='user_appointment_fk')
    appointment_days = models.IntegerField()
    site = models.ForeignKey(SiteInfo, related_name='user_appointment_site_fk')
    status_code = models.IntegerField(default=0)   # 0 已预约 1 已接订单 2 已交箱 3 使用中 4 待归还 5 已归还
    create_time = models.DateTimeField(default=datetime.datetime.today())
    cancel_time = models.DateTimeField(default=datetime.datetime.now(), null=True)


class AppointmentDetail(models.Model):
    detail_id = models.CharField(max_length=48, primary_key=True)
    appointment_id = models.ForeignKey(UserAppointment, related_name='appointment_detail_id_fk')
    box_type = models.ForeignKey(BoxTypeInfo, related_name='appointment_detail_box_type_fk')
    box_num = models.IntegerField(default=0)


class BoxOrder(models.Model):
    box_order_id = models.CharField(max_length=48, primary_key=True)
    order_start_time = models.DateTimeField(default=datetime.datetime.now())
    order_end_time = models.DateTimeField(default=datetime.datetime.now())
    state = models.IntegerField(default=0)
    ack_flag = models.IntegerField(default=0)
    user = models.ForeignKey(EnterpriseUser, related_name='box_order_user_fk')


class BoxOrderDetail(models.Model):
    order_detail_id = models.CharField(max_length=48, primary_key=True)
    order_detail_start_time = models.DateTimeField(default=datetime.datetime.now())
    order_detail_end_time = models.DateTimeField(default='')
    box_order = models.ForeignKey(BoxOrder, null=True, related_name='box_order_id_fk')
    box = models.ForeignKey(BoxInfo, null=True, related_name='box_id_fk')
    state = models.IntegerField(default=0)    # 0 已出仓库


class BoxTypeInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    box_type_name = models.CharField(max_length=128, default='')
    box_type_detail = models.CharField(max_length=128, default='')
    interval_time = models.IntegerField()
    temperature_threshold_min = models.FloatField()
    temperature_threshold_max = models.FloatField()
    humidity_threshold_min = models.FloatField()
    humidity_threshold_max = models.FloatField()
    collision_threshold_min = models.IntegerField()
    collision_threshold_max = models.IntegerField()
    battery_threshold_min = models.FloatField()
    battery_threshold_max = models.FloatField()
    operation_threshold_min = models.IntegerField()
    operation_threshold_max = models.IntegerField()
    price = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()


class SiteInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, default='')
    location = models.TextField(default='')
    latitude = models.CharField(max_length=16, default='0.0')
    longitude = models.CharField(max_length=16, default='0.0')
    site_code = models.CharField(max_length=48, default='')
    volume = models.IntegerField(default=0)
    telephone = models.CharField(max_length=20, default='')
    price = models.IntegerField(default=0)


class BoxInfo(models.Model):
    deviceid = models.CharField(max_length=48, primary_key=True)
    type = models.ForeignKey(BoxTypeInfo, related_name='box_info_box_type_fk')
    ava_flag = models.CharField(max_length=1, default='Y')
    siteinfo = models.ForeignKey(SiteInfo, related_name='box_site_fk', null=True)
    recycle_flag = models.IntegerField(default=0)


class ShopInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, default='')
    location = models.CharField(max_length=256, default='')
    latitude = models.CharField(max_length=16, default='0.0')
    longitude = models.CharField(max_length=16, default='0.0')
    site_code = models.CharField(max_length=48, default='')
    telephone = models.CharField(max_length=20, default='')


class GoodsType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, default='')


class GoodsUnit(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, default='')


class GoodsList(models.Model):
    id = models.CharField(max_length=48, primary_key=True)
    type = models.ForeignKey(GoodsType, related_name='goods_type_fk')
    unit = models.ForeignKey(GoodsUnit, related_name='goods_unit_fk')
    num = models.IntegerField(default=0)
    flag = models.IntegerField(default=0)


class GoodsOrder(models.Model):
    id = models.CharField(max_length=48, primary_key=True)
    order_start_time = models.DateTimeField(default=datetime.datetime.now())
    order_end_time = models.DateTimeField(default=datetime.datetime.now())
    state = models.IntegerField(default=0)
    site = models.ForeignKey(SiteInfo, related_name='goods_order_site')
    ack_flag = models.IntegerField(default=0)
    shop = models.ForeignKey(ShopInfo, null=True, related_name='goods_order_shop')
    user = models.ForeignKey(EnterpriseUser, related_name='goods_order_user')


class GoodsOrderDetail(models.Model):
    id = models.CharField(max_length=48, primary_key=True)
    order = models.ForeignKey(GoodsOrder, related_name='goods_order_detail_fk')
    box = models.ForeignKey(BoxInfo, related_name='goods_order_detail_box')
    ack_flag = models.IntegerField(default=0)


class OrderItem(models.Model):
    id = models.CharField(max_length=48, primary_key=True)
    goods_type = models.ForeignKey(GoodsType, null=True)
    goods_unit = models.ForeignKey(GoodsUnit, null=True)
    num = models.IntegerField(default=0)
    order_detail = models.ForeignKey(GoodsOrderDetail)


class NotifyMessage(models.Model):
    notify_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=64, default='')
    notify_time = models.DateTimeField(default=datetime.datetime.now())
    notify_title = models.CharField(max_length=50, default='')
    notify_content = models.TextField()
    read_flag = models.CharField(max_length=1, default='N')


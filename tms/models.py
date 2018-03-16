# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from util.geo import cal_position

# Create your models here.
import datetime
from django.utils import timezone
import pytz


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


# 角色
class Role(models.Model):
    role_id = models.CharField(max_length=128, default='', primary_key=True)
    role_name = models.CharField(max_length=128, default='')
    is_driver = models.IntegerField(default=0)


# 用户
class User(models.Model):
    user_id = models.CharField(max_length=128, default='', primary_key=True)
    role = models.ForeignKey(Role, related_name='user_role_fk')
    user_password = models.CharField(max_length=32)
    register_time = models.DateTimeField(default=datetime.datetime.today())
    status = models.CharField(max_length=16)
    avatar_url = models.CharField(max_length=256)
    user_phone = models.CharField(max_length=16)
    user_email = models.CharField(max_length=128)
    # enterprise = models.ForeignKey(EnterpriseInfo, related_name='enterprise_user_enterprise_info_fk', null=True)
    user_token = models.CharField(max_length=64, default='')
    group = models.ForeignKey(AccessGroup, null=True)
    user_real_name = models.CharField(max_length=48, default='')
    user_gender = models.CharField(max_length=8, default='')
    user_nickname = models.CharField(max_length=48, default='')
    user_alias_id = models.CharField(max_length=64, default='')
    user_password_encrypt = models.CharField(max_length=256, default='')


# 卡车水槽
class TruckFlume(models.Model):
    flume_id = models.CharField(max_length=128, default='', primary_key=True)
    user = models.ForeignKey(User, related_name='driver_fk')
    deviceid = models.CharField(max_length=128, default='')


# 智能硬件传感器信息
class SensorData(models.Model):
    timestamp = models.IntegerField(default=0)  # 数据时间
    intimestamp = models.IntegerField(default=0)  # 记录入库时间
    deviceid = models.CharField(max_length=128, default='')
    temperature = models.CharField(max_length=10, default='0')
    longitude = models.CharField(max_length=20, default='0')
    latitude = models.CharField(max_length=20, default='0')
    salinity = models.CharField(max_length=20, default='0')
    ph = models.CharField(max_length=20, default='0')
    dissolved_oxygen = models.CharField(max_length=20, default='0')  # 溶氧量
    chemical_oxygen_consumption = models.CharField(max_length=20, default='0')  # 化学耗氧量
    transparency = models.CharField(max_length=20, default='0')  # 透明度
    aqua = models.CharField(max_length=20, default='0')  # 水色
    nutrient_salt_of_water = models.CharField(max_length=20, default='0')  # 水体营养盐
    anaerobion = models.CharField(max_length=20, default='0')  # 厌氧菌

    def convert_longitude(self):
        return str(cal_position(self.longitude))

    def convert_latitude(self):
        return str(cal_position(self.latitude))


# 水产类型
class FishType(models.Model):
    type_id = models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=128, default='')


# 单位
class Unit(models.Model):
    unit_id = models.IntegerField(primary_key=True)
    unit_name = models.CharField(max_length=128, default='')


# 渔场
class Fishery(models.Model):
    fishery_id = models.IntegerField(primary_key=True)
    fishery_name = models.CharField(max_length=128, default='')
    longitude = models.CharField(max_length=20, default='0')
    latitude = models.CharField(max_length=20, default='0')


# 主订单表
class FishingHistory(models.Model):
    QR_id = models.CharField(max_length=128, default='', primary_key=True)
    fish_type = models.ForeignKey(FishType, related_name='fishing_history_fish_type_fk')
    fishery = models.ForeignKey(Fishery, related_name='fishing_history_fishery_fk')
    weight = models.DecimalField(decimal_places=2, max_digits=5)
    unit = models.ForeignKey(Unit, related_name='fishing_history_unit_fk')
    flume = models.ForeignKey(TruckFlume, related_name='fishing_history_flume', null=True)
    order_status = models.IntegerField(default=0)  # 订单状态, 0 创建订单  1 订单运输中  2 订单结束


# 操作流水
class OperateHistory(models.Model):
    id = models.AutoField(primary_key=True)
    qr_id = models.CharField(max_length=128, default='')
    user = models.ForeignKey(User, related_name='operate_history_user')
    timestamp = models.IntegerField
    op_type = models.IntegerField  # 操作类型: 1 捕捞 2 装车 3 商家收货








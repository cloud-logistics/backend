#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# class BoxInfo(models.Model):
#     deviceid = models.TextField()
#     type = models.IntegerField()
#     date_of_production = models.TextField()
#     manufacturer = models.IntegerField()
#     produce_area = models.IntegerField()
#     hardware = models.IntegerField()
#     battery = models.IntegerField()
#     carrier = models.IntegerField()
#
#
# class BoxTypeInfo(models.Model):
#     box_type_name = models.TextField()
#     box_type_detail = models.TextField()
#     interval_time = models.IntegerField()
#     temperature_threshold_min = models.IntegerField()
#     temperature_threshold_max = models.IntegerField()
#     humidity_threshold_min = models.IntegerField()
#     humidity_threshold_max = models.IntegerField()
#     collision_threshold_min = models.IntegerField()
#     collision_threshold_max = models.IntegerField()
#     battery_threshold_min = models.IntegerField()
#     battery_threshold_max = models.IntegerField()
#     operation_threshold_min = models.IntegerField()
#     operation_threshold_max = models.IntegerField()
#
#
# class CarrierInfo(models.Model):
#     carrier_name = models.TextField()
#
#
# class BoxOrderRelation(models.Model):
#     trackid = models.TextField()
#     deviceid = models.TextField()
#
#
# class OrderInfo(models.Model):
#     srcid = models.IntegerField()
#     dstid = models.IntegerField()
#     trackid = models.TextField()
#     starttime = models.TextField()
#     endtime = models.TextField()
#     carrierid = models.IntegerField()
#
#
# class SiteInfo(models.Model):
#     location = models.TextField()
#     latitude = models.TextField()
#     longitude = models.TextField()
#
#
# class AlertLevelInfo(models.Model):
#     level = models.TextField()
#
#
# class AlertTypeInfo(models.Model):
#     type = models.TextField()
#
#
# class AlertCodeInfo(models.Model):
#     errcode = models.IntegerField()
#     description = models.TextField()
#
#
# class BatteryInfo(models.Model):
#     battery_detail = models.TextField()
#
#
# class MaintenanceInfo(models.Model):
#     location = models.TextField()
#
#
# class IntervalTimeInfo(models.Model):
#     interval_time_min = models.IntegerField()
#
#
# class HardwareInfo(models.Model):
#     hardware_detail = models.TextField()
#
#
# class ManufacturerInfo(models.Model):
#     name = models.TextField()
#
#
# class ProduceAreaInfo(models.Model):
#     address = models.TextField()
#
#
# class AlarmInfo(models.Model):
#     timestamp = models.IntegerField()
#     deviceid = models.TextField()
#     level = models.IntegerField()
#     code = models.IntegerField()
#     status = models.TextField()
#     carrier = models.IntegerField()
#     longitude = models.TextField()
#     latitude = models.TextField()
#     speed = models.TextField()
#     temperature = models.TextField()
#     humidity = models.TextField()
#     num_of_collide = models.TextField()
#     num_of_door_open = models.TextField()
#     battery = models.TextField()
#     robert_operation_status = models.TextField()
# 国家
class Nation(models.Model):
    nation_id = models.AutoField(primary_key=True)
    nation_name = models.CharField(max_length=100, default='')
    pic_url = models.CharField(max_length=200, default='')
    sorted_key = models.CharField(max_length=10, default='')


# 省
class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    province_name = models.CharField(max_length=100, default='')
    zip_code = models.CharField(max_length=10, default='')
    nation = models.ForeignKey(Nation, related_name='province_nation_fk', default=1)


# 城市
class City(models.Model):
    city_name = models.CharField(max_length=50)
    state_name = models.CharField(max_length=50)
    nation_name = models.CharField(max_length=50)
    longitude = models.CharField(max_length=20)
    latitude = models.CharField(max_length=20)
    area_name = models.CharField(max_length=10)
    culture = models.TextField(default='')
    taboo = models.TextField(default='')
    picture_url = models.CharField(max_length=200, default='')
    nation = models.ForeignKey(Nation, related_name='city_fk')
    sorted_key = models.CharField(max_length=10, default='')
    flag = models.IntegerField(default=0)  # 酒店
    province = models.ForeignKey(Province, related_name='city_province_fk', null=True)


class ContainerRentInfo(models.Model):
    deviceid = models.TextField()
    starttime = models.TextField()
    endtime = models.TextField()
    carrier = models.IntegerField()
    type = models.IntegerField()
    owner = models.TextField()
    rentstatus = models.IntegerField()

    class Meta:
        permissions = (
            ("view_containerrentinfo", "Can see container rent info"),
        )


class SiteInfo(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, default='')
    location = models.TextField(default='')
    latitude = models.CharField(max_length=16, default='0.0')
    longitude = models.CharField(max_length=16, default='0.0')
    site_code = models.CharField(max_length=48, default='')
    city = models.ForeignKey(City, related_name='site_city_fk', default=1)
    province = models.ForeignKey(Province, related_name='site_province_fk', default=1)
    nation = models.ForeignKey(Nation, related_name='site_nation_fk', default=1)
    volume = models.IntegerField(default=0)


class SiteHistory(models.Model):
    timestamp = models.IntegerField()
    site_id = models.IntegerField()
    box_id = models.CharField(max_length=48, default='')
    op_type = models.IntegerField(default=0)


class BoxTypeInfo(models.Model):
    id = models.AutoField(primary_key=True)
    box_type_name = models.CharField(max_length=128, default='')
    box_type_detail = models.CharField(max_length=128, default='')
    interval_time = models.IntegerField()
    temperature_threshold_min = models.IntegerField()
    temperature_threshold_max = models.IntegerField()
    humidity_threshold_min = models.IntegerField()
    humidity_threshold_max = models.IntegerField()
    collision_threshold_min = models.IntegerField()
    collision_threshold_max = models.IntegerField()
    battery_threshold_min = models.IntegerField()
    battery_threshold_max = models.IntegerField()
    operation_threshold_min = models.IntegerField()
    operation_threshold_max = models.IntegerField()
    price = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()


# 制造商
class Manufacturer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)


# 生产地
class ProduceArea(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=128)


# 硬件
class Hardware(models.Model):
    id = models.AutoField(primary_key=True)
    hardware_detail = models.CharField(max_length=128)


# 电源
class Battery(models.Model):
    id = models.AutoField(primary_key=True)
    battery_detail = models.CharField(max_length=128)


class BoxInfo(models.Model):
    deviceid = models.CharField(max_length=48, primary_key=True)
    type = models.ForeignKey(BoxTypeInfo, related_name='box_info_box_type_fk')
    date_of_production = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Manufacturer, related_name='box_info_box_man_fk', null=True)
    produce_area = models.ForeignKey(ProduceArea, related_name='box_info_box_pro_fk', null=True)
    hardware = models.ForeignKey(Hardware, related_name='box_info_box_hard_fk', null=True)
    battery = models.ForeignKey(Battery, related_name='box_info_box_bat_fk', null=True)
    carrier = models.IntegerField()
    tid = models.CharField(max_length=48)
    ava_flag = models.CharField(max_length=1, default='Y')
    siteinfo = models.ForeignKey(SiteInfo, related_name='box_site_fk', null=True)


# 传感器数据
class SensorData(models.Model):
    timestamp = models.IntegerField()
    deviceid = models.CharField(max_length=48)
    temperature = models.CharField(max_length=10)
    humidity = models.CharField(max_length=10)
    longitude = models.CharField(max_length=20)
    latitude = models.CharField(max_length=20)
    speed = models.CharField(max_length=20)
    collide = models.CharField(max_length=10)
    light = models.CharField(max_length=10)
    legacy = models.TextField(default='')
    endpointid = models.CharField(max_length=48)


# 仓库各类型可用箱子数量
class SiteBoxStock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    site = models.ForeignKey(SiteInfo, related_name='stock_site_fk')
    box_type = models.ForeignKey(BoxTypeInfo, related_name='stock_box_type_fk')
    ava_num = models.IntegerField(default=0)  # 可用数量
    reserve_num = models.IntegerField(default=0)  # 预约数量

    class Meta:
        unique_together = ('site', 'box_type',)


# 堆场调度信息
class SiteDispatch(models.Model):
    did = models.AutoField(primary_key=True)
    start = models.ForeignKey(SiteInfo, related_name='start_site_fk')
    finish = models.ForeignKey(SiteInfo, related_name='finish_site_fk')
    count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='undispatch')
    create_date = models.DateField()


# 系统用户组
class SysGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=50)


# 系统用户
class SysUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=20)
    user_password = models.CharField(max_length=20)
    user_token = models.CharField(max_length=64, )
    sys_group = models.ForeignKey(SysGroup, related_name='user_group_fk', null=True)


# 系统用户组可访问url
class SysAccessUrl(models.Model):
    access_url_id = models.AutoField(primary_key=True)
    access_url = models.CharField(max_length=128)
    sys_group = models.ForeignKey(SysGroup, related_name='url_group_fk', null=True)



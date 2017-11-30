#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from monservice.models import BoxTypeInfo, BoxInfo, SiteInfo
import datetime
from django.utils import timezone
import pytz

# Create your models here.
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


class RentalServiceAdmin(models.Model):
    user_id = models.CharField(max_length=48, primary_key=True)
    user_name = models.CharField(max_length=48)
    user_password = models.CharField(max_length=32)
    register_time = models.DateTimeField(default=datetime.datetime.today())
    status = models.CharField(max_length=16)
    avatar_url = models.CharField(max_length=256)
    user_phone = models.CharField(max_length=16)
    user_email = models.CharField(max_length=128)
    user_token = models.CharField(max_length=64, default='')
    group = models.ForeignKey(AccessGroup, related_name='enterprise_user_fk')


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
    group = models.ForeignKey(AccessGroup, null=True)
    user_real_name = models.CharField(max_length=48, default='')
    user_gender = models.CharField(max_length=8, default='')
    user_nickname = models.CharField(max_length=48, default='')
    user_alias_id = models.CharField(max_length=64, default='')
    user_password_encrypt = models.CharField(max_length=256, default='')


class UserAppointment(models.Model):
    appointment_id = models.CharField(max_length=48, primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser, related_name='user_appointment_fk')
    appointment_time = models.DateTimeField(default=datetime.datetime.today())
    appointment_code = models.CharField(max_length=48, default='')
    flag = models.IntegerField(default=0)
    cancel_time = models.DateTimeField(default=datetime.datetime.now(), null=True)


class AppointmentDetail(models.Model):
    detail_id = models.CharField(max_length=48, primary_key=True)
    appointment_id = models.ForeignKey(UserAppointment, related_name='appointment_detail_id_fk')
    box_type = models.ForeignKey(BoxTypeInfo, related_name='appointment_detail_box_type_fk')
    box_num = models.IntegerField(default=0)
    site_id = models.ForeignKey(SiteInfo)
    flag = models.IntegerField(default=0)


class RentLeaseInfo(models.Model):
    lease_info_id = models.CharField(max_length=48, primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser)
    lease_start_time = models.DateTimeField(default=datetime.datetime.now())
    lease_end_time = models.DateTimeField(null=True)
    lease_admin_off = models.ForeignKey(RentalServiceAdmin, null=True, related_name='lease_admin_off_fk')
    lease_admin_on = models.ForeignKey(RentalServiceAdmin, null=True, related_name='lease_admin_on_fk')
    box = models.ForeignKey(BoxInfo, null=True, related_name='box_id_fk')
    off_site = models.ForeignKey(SiteInfo, null=True, related_name='off_site_fk')
    on_site = models.ForeignKey(SiteInfo, null=True, related_name='on_site_fk')
    rent = models.BigIntegerField(default=0)
    rent_status = models.IntegerField(default=0)
    rent_fee_rate = models.BigIntegerField(default=0)
    last_update_time = models.DateTimeField(null=True)
    sum_flag = models.IntegerField(default=0)


class RentalAdminOperationRecords(models.Model):
    record_id = models.CharField(max_length=48, primary_key=True)
    admin_id = models.ForeignKey(RentalServiceAdmin, related_name='rental_admin_operation_record_rental_admin_id_fk')
    operation_detail = models.CharField(max_length=128, default='')
    flag = models.IntegerField(default=0)


class AppointmentCodeSeq(models.Model):
    """
        This class maps to OrderNumberSeq which is a PostgreSQL sequence.
        This sequence runs from 1 to 9999 after which it restarts (cycles) at 1.
        A sequence is basically a special single row table.
        """
    sequence_name = models.CharField(max_length=128, primary_key=True)
    last_value = models.IntegerField()
    increment_by = models.IntegerField()
    max_value = models.IntegerField()
    min_value = models.IntegerField()
    cache_value = models.IntegerField()
    log_cnt = models.IntegerField()
    is_cycled = models.BooleanField()
    is_called = models.BooleanField()

    class Meta:
        db_table = u'iot.appointment_code'


class SiteStat(models.Model):
    stat_id = models.CharField(max_length=48, primary_key=True)
    stat_day = models.CharField(max_length=10, default='')
    total_in = models.IntegerField(default=0)
    total_out = models.IntegerField(default=0)
    site = models.ForeignKey(SiteInfo, related_name='stat_site_fk', null=True)


class SiteStatDetail(models.Model):
    detail_id = models.CharField(max_length=48, primary_key=True)
    box_type = models.ForeignKey(BoxTypeInfo, related_name='stat_detail_box_type_fk', null=True)
    box_in = models.IntegerField(default=0)
    box_out = models.IntegerField(default=0)
    sitestat = models.ForeignKey(SiteStat, related_name='detail_stat_fk', null=True)


class BoxRentFeeDetail(models.Model):
    detail_id = models.CharField(max_length=48, primary_key=True)
    enterprise = models.ForeignKey(EnterpriseInfo, null=True)
    user = models.ForeignKey(EnterpriseUser, null=True)
    date = models.DateTimeField(default=datetime.datetime.today())
    off_site_nums = models.BigIntegerField(default=0)
    on_site_nums = models.BigIntegerField(default=0)
    rent_fee = models.BigIntegerField(default=0)


class BoxRentFeeByMonth(models.Model):
    detail_id = models.CharField(max_length=48, primary_key=True)
    enterprise = models.ForeignKey(EnterpriseInfo, null=True)
    date = models.DateTimeField(default=datetime.datetime.today())
    off_site_nums = models.BigIntegerField(default=0)
    on_site_nums = models.BigIntegerField(default=0)
    rent_fee = models.BigIntegerField(default=0)


class NotifyMessage(models.Model):
    notify_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(EnterpriseUser, related_name='notify_enterprise_fk', null=True)
    notify_time = models.DateTimeField(default=datetime.datetime.now())
    notify_title = models.CharField(max_length=50, default='')
    notify_content = models.TextField()
    read_flag = models.CharField(max_length=1, default='N')


class Param(models.Model):
    param_key = models.CharField(max_length=50, unique=True)
    param_value = models.CharField(max_length=50, default="")
    param_desc = models.CharField(max_length=100, default="")

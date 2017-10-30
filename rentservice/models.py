from __future__ import unicode_literals

from django.db import models
from monservice.models import BoxTypeInfo, BoxInfo, SiteInfo
import datetime
from django.utils import timezone


# Create your models here.


class AccessGroup(models.Model):
    access_group_id = models.CharField(max_length=64, primary_key=True)
    group = models.CharField(max_length=32)


class AuthUserGroup(models.Model):
    auth_id = models.AutoField(primary_key=True)
    user_token = models.CharField(max_length=64)
    group = models.ForeignKey(AccessGroup, related_name='auth_user_group_fk')


class AccessUrlGroup(models.Model):
    access_url_id = models.AutoField(primary_key=True)
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
    register_time = models.DateTimeField(default=datetime.datetime.today())


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
    enterprise = models.ForeignKey(EnterpriseInfo, related_name='enterprise_user_enterprise_info_fk')
    user_token = models.CharField(max_length=64, default='')
    role = models.CharField(max_length=16, default='user')
    group = models.ForeignKey(AccessGroup, null=True)


class UserAppointment(models.Model):
    appointment_id = models.CharField(max_length=48, primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser, related_name='user_appointment_fk')
    appointment_time = models.DateTimeField(default=datetime.datetime.today())
    appointment_code = models.CharField(max_length=48, default='')


class AppointmentDetail(models.Model):
    detail_id = models.CharField(max_length=48, primary_key=True)
    appointment_id = models.ForeignKey(UserAppointment, related_name='appointment_detail_id_fk')
    box_type = models.ForeignKey(BoxTypeInfo, related_name='appointment_detail_box_type_fk')
    box_num = models.IntegerField(default=0)
    site_id = models.ForeignKey(SiteInfo)


class UserLeaseInfo(models.Model):
    user_lease_info_id = models.CharField(max_length=48, primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser, related_name='user_lease_info_enterprise_user_fk')
    lease_start_time = models.DateTimeField()
    lease_end_time = models.DateTimeField()
    lease_admin_off = models.CharField(max_length=48)
    lease_admin_on = models.CharField(max_length=48)
    box_id = models.ForeignKey(BoxInfo, related_name='user_lease_info_box_info_fk')
    off_site_id = models.IntegerField()
    on_site_id = models.IntegerField()
    rent = models.BigIntegerField(default=0)


class UserRentDay(models.Model):
    user_rent_day_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser, related_name='user_rent_day_enterprise_user_fk')
    enterprise_id = models.ForeignKey(EnterpriseInfo, related_name='user_rent_day_enterprise_info_fk')
    date = models.DateField()
    rent = models.BigIntegerField(default=0)


class UserRentMonth(models.Model):
    user_rent_month_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(EnterpriseUser, related_name='user_rent_month_enterprise_user_fk')
    enterprise_id = models.ForeignKey(EnterpriseInfo, related_name='user_rent_month_enterprise_info_fk')
    month = models.DateField()
    rent = models.BigIntegerField(default=0)


class RentalAdminOperationType(models.Model):
    type_id = models.CharField(max_length=48, primary_key=True)
    operation_name = models.CharField(max_length=128, default='default operation')


class RentalAdminOperationRecords(models.Model):
    record_id = models.CharField(max_length=48, primary_key=True)
    admin_id = models.ForeignKey(RentalServiceAdmin, related_name='rental_admin_operation_record_rental_admin_id_fk')
    operation = models.ForeignKey(RentalAdminOperationType, related_name='rental_admin_operation_record_oper_type_fk')
    flag = models.IntegerField(default=0)


class RentServiceRegUser(models.Model):
    reg_user_id = models.CharField(max_length=64, primary_key=True)
    user_name = models.CharField(max_length=64)
    user_password = models.CharField(max_length=128)
    user_token = models.CharField(max_length=64)





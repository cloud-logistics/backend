#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework import serializers
from models import AccessGroup
from models import AuthUserGroup
from models import AccessUrlGroup
from models import EnterpriseInfo
from models import RentalServiceAdmin
from models import UserAppointment
from models import EnterpriseUser
from models import AppointmentDetail
from models import UserLeaseInfo
from models import UserRentDay
from models import UserRentMonth
from models import RentalAdminOperationType
from models import RentalAdminOperationRecords
from models import RentServiceRegUser



class AccessGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessGroup
        fields = '__all__'


class AuthUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUserGroup
        fields = '__all__'


class AccessUrlGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessUrlGroup
        fields = '__all__'


class EnterpriseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseInfo
        fields = '__all__'


class RentalServiceAdmin(serializers.ModelSerializer):
    class Meta:
        model = RentalServiceAdmin
        fields = '__all__'


class EnterpriseUser(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseUser
        fields = '__all__'


class UserAppointment(serializers.ModelSerializer):
    class Meta:
        model = UserAppointment
        fields = '__all__'


class AppointmentDetail(serializers.ModelSerializer):
    class Meta:
        model = AppointmentDetail
        fields = '__all__'


class UserLeaseInfo(serializers.ModelSerializer):
    class Meta:
        model = UserLeaseInfo
        fields = '__all__'


class UserRentDay(serializers.ModelSerializer):
    class Meta:
        model = UserRentDay
        fields = '__all__'


class UserRentMonth(serializers.ModelSerializer):
    class Meta:
        model = UserRentMonth
        fields = '__all__'


class RentalAdminOperationType(serializers.ModelSerializer):
    class Meta:
        model = RentalAdminOperationType
        fields = '__all__'


class RentalAdminOperationRecords(serializers.ModelSerializer):
    class Meta:
        model = RentalAdminOperationRecords
        fields = '__all__'


class RentServiceRegUser(serializers.ModelSerializer):
    class Meta:
        model = RentServiceRegUser

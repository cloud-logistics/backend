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
from models import RentLeaseInfo
from models import UserRentDay
from models import UserRentMonth
from models import RentalAdminOperationRecords


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


class RentalServiceAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalServiceAdmin
        fields = '__all__'


class EnterpriseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseUser
        fields = '__all__'


class UserAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAppointment
        fields = '__all__'


class AppointmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentDetail
        fields = '__all__'


class RentLeaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentLeaseInfo
        fields = '__all__'


class UserRentDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRentDay
        fields = '__all__'


class UserRentMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRentMonth
        fields = '__all__'


# class RentalAdminOperationType(serializers.ModelSerializer):
#     class Meta:
#         model = RentalAdminOperationType
#         fields = '__all__'


class RentalAdminOperationRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalAdminOperationRecords
        fields = '__all__'

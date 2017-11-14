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
from monservice.models import BoxTypeInfo
from monservice.models import SiteInfo
from monservice.models import BoxInfo
from models import SiteStat
from models import SiteStatDetail


class BoxTypeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxTypeInfo
        fields = '__all__'


class SiteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = '__all__'


class BoxInfoSerializer(serializers.ModelSerializer):
    type = BoxTypeInfoSerializer()
    siteinfo = SiteInfoSerializer()

    class Meta:
        model = BoxInfo
        fields = '__all__'


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
        exclude = ('user_password',)


class EnterpriseUserForeignKeySerializer(serializers.ModelSerializer):
    group = AccessGroupSerializer(read_only=True)['group']
    enterprise = EnterpriseInfoSerializer(read_only=True)['enterprise_id']

    class Meta:
        model = EnterpriseUser
        fields = ('user_id', 'user_name', 'user_password', 'register_time', 'status', 'avatar_url',
                  'user_phone', 'user_email', 'enterprise', 'user_token', 'role', 'group')


class UserAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAppointment
        fields = '__all__'


class AppointmentDetailSerializer(serializers.ModelSerializer):
    box_type = BoxTypeInfoSerializer()

    class Meta:
        model = AppointmentDetail
        fields = '__all__'


class RentLeaseInfoSerializer(serializers.ModelSerializer):
    box = BoxInfoSerializer()
    on_site = SiteInfoSerializer()
    off_site = SiteInfoSerializer()

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


class RentalAdminOperationRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalAdminOperationRecords
        fields = '__all__'


class AppSiteSerializer(serializers.ModelSerializer):
    box_info = AppointmentDetailSerializer(many=True)

    class Meta:
        model = SiteInfo
        fields = '__all__'


class AppointmentResSerializer(serializers.ModelSerializer):
    info = AppSiteSerializer(many=True)

    class Meta:
        model = UserAppointment
        fields = '__all__'


class SiteStatSerializer(serializers.ModelSerializer):
    site = SiteInfoSerializer()

    class Meta:
        model = SiteStat
        fields = '__all__'


class SiteStatDetailSerializer(serializers.ModelSerializer):
    box_type = BoxTypeInfoSerializer()

    class Meta:
        model = SiteStatDetail
        fields = '__all__'


class SiteStatResSerializer(serializers.ModelSerializer):
    detail = SiteStatDetailSerializer(many=True)

    class Meta:
        model = SiteStat
        fields = '__all__'

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
from models import RentalAdminOperationRecords
from monservice.models import BoxTypeInfo
from monservice.models import SiteInfo
from monservice.models import BoxInfo
from monservice.models import Manufacturer, ProduceArea, Hardware, Battery
from models import SiteStat
from models import SiteStatDetail
from models import BoxRentFeeDetail
from models import NotifyMessage
from models import BoxRentFeeByMonth
from models import Param


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class ProduceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduceArea
        fields = '__all__'


class HardwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hardware
        fields = '__all__'


class BatterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Battery
        fields = '__all__'


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
        exclude = ('user_password', 'user_password_encrypt')


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
    site_id = SiteInfoSerializer()

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


class BoxInfoResSerializer(serializers.ModelSerializer):
    type = BoxTypeInfoSerializer()
    siteinfo = SiteInfoSerializer()
    manufacturer = ManufacturerSerializer()
    produce_area = ProduceAreaSerializer()
    hardware = HardwareSerializer()
    battery = BatterySerializer()
    rent_status = serializers.SerializerMethodField()

    class Meta:
        model = BoxInfo
        fields = '__all__'

    def get_rent_status(self, obj):
        rent_status = 0
        status = RentLeaseInfo.objects.filter(box=obj, rent_status=0).count()
        if status == 0 and obj.siteinfo is None:
            rent_status = 2
        elif status == 1:
            rent_status = 1
        if obj.ava_flag == 'N':
            rent_status = 2
        return rent_status


class RentLeaseBoxSerializer(serializers.ModelSerializer):
    box = BoxInfoSerializer()
    on_site = SiteInfoSerializer()
    off_site = SiteInfoSerializer()
    enterprise = serializers.SerializerMethodField()

    class Meta:
        model = RentLeaseInfo
        fields = '__all__'

    def get_enterprise(self, obj):
        return EnterpriseInfoSerializer(obj.user_id.enterprise).data


class BoxRentFeeDetailSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseInfoSerializer()
    user = EnterpriseUserSerializer()

    class Meta:
        model = BoxRentFeeDetail
        fields = '__all__'


class NotifyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyMessage
        fields = '__all__'


class BoxRentFeeByMonthSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseInfoSerializer()

    class Meta:
        model = BoxRentFeeByMonth
        fields = '__all__'


class AllSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = ('id', 'name')


class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = '__all__'


class BoxInfoListSerializer(serializers.ModelSerializer):
    type = BoxTypeInfoSerializer()
    siteinfo = SiteInfoSerializer()
    rent_status = serializers.SerializerMethodField()

    class Meta:
        model = BoxInfo
        fields = '__all__'

    def get_rent_status(self, obj):
        rent_status = 0
        status = RentLeaseInfo.objects.filter(box=obj, rent_status=0).count()
        if status == 0 and obj.siteinfo is None:
            rent_status = 2
        elif status == 1:
            rent_status = 1
        if obj.ava_flag == 'N':
            rent_status = 2
        return rent_status

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from tms.models import SensorData
from rest_framework import serializers
from tms.models import AccessGroup
from tms.models import AuthUserGroup
from tms.models import AccessUrlGroup
from tms.models import User
from tms.models import NotifyMessage
from tms.models import FishType


class SensorDataSerializer(serializers.ModelSerializer):
    longitude = serializers.ReadOnlyField(source='convert_longitude')
    latitude = serializers.ReadOnlyField(source='convert_latitude')

    class Meta:
        model = SensorData
        fields = ('timestamp', 'intimestamp', 'deviceid', 'temperature',
                  'longitude', 'latitude', 'salinity', 'ph', 'dissolved_oxygen',
                  'chemical_oxygen_consumption', 'transparency', 'aqua',
                  'nutrient_salt_of_water', 'anaerobion')


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

#
# class EnterpriseInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EnterpriseInfo
#         fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('user_password', 'user_password_encrypt')


class NotifyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyMessage
        fields = '__all__'


class SensorPathDataSerializer(serializers.ModelSerializer):
    longitude = serializers.ReadOnlyField(source='convert_longitude')
    latitude = serializers.ReadOnlyField(source='convert_latitude')

    class Meta:
        model = SensorData
        fields = ('timestamp', 'longitude', 'latitude')


class FishTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FishType
        fields = '__all__'

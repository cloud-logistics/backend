#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework import serializers
from smarttms.models import AccessGroup
from smarttms.models import AuthUserGroup
from smarttms.models import AccessUrlGroup
from smarttms.models import EnterpriseInfo
from smarttms.models import EnterpriseUser
from smarttms.models import BoxTypeInfo
from smarttms.models import SiteInfo
from smarttms.models import BoxInfo
from smarttms.models import NotifyMessage
from smarttms.models import GoodsOrder, GoodsOrderDetail, ShopInfo


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


class BoxInfoResSerializer(serializers.ModelSerializer):
    type = BoxTypeInfoSerializer()
    siteinfo = SiteInfoSerializer()

    class Meta:
        model = BoxInfo
        fields = '__all__'


class NotifyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyMessage
        fields = '__all__'


class ShopInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopInfo
        fields = '__all__'


class GoodsOrderSerializer(serializers.ModelSerializer):
    site = SiteInfoSerializer()
    shop = ShopInfoSerializer()
    user = EnterpriseUserSerializer()

    class Meta:
        model = GoodsOrder
        fields = '__all__'


class GoodsOrderDetailSerializer(serializers.ModelSerializer):
    order = GoodsOrderSerializer()
    box = BoxInfoSerializer()

    class Meta:
        model = GoodsOrderDetail
        fields = '__all__'

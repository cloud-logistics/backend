from rest_framework import serializers
from models import ContainerRentInfo
from models import SiteInfo


class ContainerRentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerRentInfo
        fields = '__all__'


class SiteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = '__all__'

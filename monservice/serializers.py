from rest_framework import serializers
from models import ContainerRentInfo
from models import SiteInfo
from models import SiteHistory
from models import Nation
from models import City
from models import BoxTypeInfo
from models import BoxInfo
from models import Province
from models import SiteBoxStock


class ContainerRentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerRentInfo
        fields = '__all__'


class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = '__all__'


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class SiteInfoSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = SiteInfo
        fields = '__all__'


class SiteHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteHistory
        fields = '__all__'


class BoxTypeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxTypeInfo
        fields = '__all__'


class SiteBoxStockSerializer(serializers.ModelSerializer):
    box_type = BoxTypeInfoSerializer()

    class Meta:
        model = SiteBoxStock
        fields = '__all__'


class SiteInfoMoreSerializer(serializers.ModelSerializer):
    box_num = SiteBoxStockSerializer(many=True)

    class Meta:
        model = SiteInfo
        fields = '__all__'

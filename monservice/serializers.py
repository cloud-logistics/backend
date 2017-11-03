from rest_framework import serializers
from models import ContainerRentInfo
from models import SiteInfo
from models import SiteHistory
from models import Nation
from models import City
from models import BoxTypeInfo
from models import BoxInfo
from models import Province
from models import SiteDispatch
from models import Manufacturer, ProduceArea, Hardware, Battery



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


class BoxInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxInfo
        fields = '__all__'


class BoxTypeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxTypeInfo
        fields = '__all__'


class SiteDispatchSerializer(serializers.ModelSerializer):

    start = SiteInfoSerializer()
    finish = SiteInfoSerializer()

    class Meta:
        model = SiteDispatch
        fields = '__all__'


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


class BoxFullInfoSerializer(serializers.ModelSerializer):
    type = BoxTypeInfoSerializer()
    manufacturer = ManufacturerSerializer()
    produce_area = ProduceAreaSerializer()
    hardware =HardwareSerializer()
    battery = BatterySerializer()
    siteinfo = SiteInfoSerializer()

    class Meta:
        model = BoxInfo
        fields = '__all__'


class SiteFullInfoSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    province = ProvinceSerializer()
    nation = NationSerializer()

    class Meta:
        model = SiteInfo
        fields = '__all__'

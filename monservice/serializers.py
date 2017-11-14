from rest_framework import serializers
from django.db import models
from models import ContainerRentInfo
from models import SiteInfo
from models import SiteHistory
from models import Nation
from models import City
from models import BoxTypeInfo
from models import BoxInfo
from models import Province
from models import SiteBoxStock
from models import SiteDispatch
from models import Manufacturer, ProduceArea, Hardware, Battery, AlarmInfo, SensorData
from models import SysGroup, SysUser, SysAccessUrl


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


class SiteBoxStockSerializer(serializers.ModelSerializer):
    box_type = BoxTypeInfoSerializer()

    class Meta:
        model = SiteBoxStock
        fields = '__all__'


class SiteInfoMoreSerializer(serializers.ModelSerializer):
    box_num = SiteBoxStockSerializer(many=True)
    city = CitySerializer()

    class Meta:
        model = SiteInfo
        fields = '__all__'


class SiteBareInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = ('id', 'location', 'longitude', 'latitude', 'site_code')


class SiteDispatchSerializer(serializers.ModelSerializer):
    start = SiteBareInfoSerializer()
    finish = SiteBareInfoSerializer()

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
    hardware = HardwareSerializer()
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


class SysGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysGroup
        fields = '__all__'


class SysUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = '__all__'


class SysAccessUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysAccessUrl
        fields = '__all__'


class RetAlarmSerializer(serializers.ModelSerializer):
    error_description = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = AlarmInfo
        fields = '__all__'

    def get_error_description(self, obj):
        return obj['error_description']

    def get_location_name(self, obj):
        return obj['location_name']


class BoxBasicInfoSerializer(serializers.ModelSerializer):
    box_type_name = serializers.SerializerMethodField()
    produce_area = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()

    class Meta:
        model = BoxInfo
        fields = ('deviceid', 'tid', 'date_of_production', 'box_type_name', 'produce_area', 'manufacturer')

    def get_box_type_name(self, obj):
        return obj['box_type_name']

    def get_produce_area(self, obj):
        return obj['produce_area']

    def get_manufacturer(self, obj):
        return obj['manufacturer']


class BoxSummarySerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()
    battery = serializers.SerializerMethodField()
    num_of_door_open = serializers.SerializerMethodField()
    robot_operation_status = serializers.SerializerMethodField()

    class Meta:
        model = SensorData
        fields = ('deviceid', 'longitude', 'latitude', 'speed', 'temperature', 'humidity', 'collide',
                  'num_of_door_open', 'robot_operation_status', 'battery', 'location_name')

    def get_location_name(self, obj):
        return obj['location_name']

    def get_battery(self, obj):
        return obj['battery']

    def get_num_of_door_open(self, obj):
        return obj['num_of_door_open']

    def get_robot_operation_status(self, obj):
        return obj['robot_operation_status']



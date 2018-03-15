# -*- coding: utf-8 -*-

from rest_framework import serializers
from tms.models import SensorData


class SensorDataSerializer(serializers.ModelSerializer):
    longitude = serializers.ReadOnlyField(source='convert_longitude')
    latitude = serializers.ReadOnlyField(source='convert_latitude')

    class Meta:
        model = SensorData
        fields = ('timestamp', 'intimestamp', 'deviceid', 'temperature',
                  'longitude', 'latitude', 'salinity', 'ph', 'dissolved_oxygen',
                  'chemical_oxygen_consumption', 'transparency', 'aqua',
                  'nutrient_salt_of_water', 'anaerobion')


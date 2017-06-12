from rest_framework import serializers
from models import ContainerRentInfo


class ContainerRentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerRentInfo
        fields = '__all__'


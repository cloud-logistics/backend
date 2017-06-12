from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# class BoxInfo(models.Model):
#     deviceid = models.TextField()
#     type = models.IntegerField()
#     date_of_production = models.TextField()
#     manufacturer = models.IntegerField()
#     produce_area = models.IntegerField()
#     hardware = models.IntegerField()
#     battery = models.IntegerField()
#     carrier = models.IntegerField()
#
#
# class BoxTypeInfo(models.Model):
#     box_type_name = models.TextField()
#     box_type_detail = models.TextField()
#     interval_time = models.IntegerField()
#     temperature_threshold_min = models.IntegerField()
#     temperature_threshold_max = models.IntegerField()
#     humidity_threshold_min = models.IntegerField()
#     humidity_threshold_max = models.IntegerField()
#     collision_threshold_min = models.IntegerField()
#     collision_threshold_max = models.IntegerField()
#     battery_threshold_min = models.IntegerField()
#     battery_threshold_max = models.IntegerField()
#     operation_threshold_min = models.IntegerField()
#     operation_threshold_max = models.IntegerField()
#
#
# class CarrierInfo(models.Model):
#     carrier_name = models.TextField()
#
#
# class BoxOrderRelation(models.Model):
#     trackid = models.TextField()
#     deviceid = models.TextField()
#
#
# class OrderInfo(models.Model):
#     srcid = models.IntegerField()
#     dstid = models.IntegerField()
#     trackid = models.TextField()
#     starttime = models.TextField()
#     endtime = models.TextField()
#     carrierid = models.IntegerField()
#
#
# class SiteInfo(models.Model):
#     location = models.TextField()
#     latitude = models.TextField()
#     longitude = models.TextField()
#
#
# class AlertLevelInfo(models.Model):
#     level = models.TextField()
#
#
# class AlertTypeInfo(models.Model):
#     type = models.TextField()
#
#
# class AlertCodeInfo(models.Model):
#     errcode = models.IntegerField()
#     description = models.TextField()
#
#
# class BatteryInfo(models.Model):
#     battery_detail = models.TextField()
#
#
# class MaintenanceInfo(models.Model):
#     location = models.TextField()
#
#
# class IntervalTimeInfo(models.Model):
#     interval_time_min = models.IntegerField()
#
#
# class HardwareInfo(models.Model):
#     hardware_detail = models.TextField()
#
#
# class ManufacturerInfo(models.Model):
#     name = models.TextField()
#
#
# class ProduceAreaInfo(models.Model):
#     address = models.TextField()
#
#
# class AlarmInfo(models.Model):
#     timestamp = models.IntegerField()
#     deviceid = models.TextField()
#     level = models.IntegerField()
#     code = models.IntegerField()
#     status = models.TextField()
#     carrier = models.IntegerField()
#     longitude = models.TextField()
#     latitude = models.TextField()
#     speed = models.TextField()
#     temperature = models.TextField()
#     humidity = models.TextField()
#     num_of_collide = models.TextField()
#     num_of_door_open = models.TextField()
#     battery = models.TextField()
#     robert_operation_status = models.TextField()


class ContainerRentInfo(models.Model):
    deviceid = models.TextField()
    starttime = models.TextField()
    endtime = models.TextField()
    carrier = models.IntegerField()
    type = models.IntegerField()

    class Meta:
        permissions = (
            ("view_containerrentinfo", "Can see container rent info"),
        )



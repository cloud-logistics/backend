#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from rest_framework import status
from util.db import query_list
from util.geo import cal_position
from rest_framework.decorators import api_view
import json


# 可用集装箱列表
@api_view(['POST'])
def available_containers(request):
    parameters = json.loads(request.body)
    latitude = parameters['lat']
    longitude = parameters['lng']
    ret_list = []
    data = query_list('select D.deviceid,D.id as type_id,E.latitude,E.longitude from '
                      '(select A.deviceid,box_type_info.box_type_name,box_type_info.id from '
                      '(select box_info.deviceid,box_info.type from iot.box_info box_info where box_info.deviceid not in '
                      '(select deviceid from iot.monservice_containerrentinfo where rentstatus = 1)) A '
                      'left join iot.box_type_info box_type_info on A.type = box_type_info.id) D '
                      'inner join '
                      '(select B.* from (select max(timestamp) as timestamp ,deviceid from iot.sensor_data group by deviceid) A '
                      'left join iot.sensor_data B '
                      'on A.timestamp = B.timestamp and A.deviceid = B.deviceid) E '
                      'on D.deviceid = E.deviceid '
                      'where iot.fn_cal_distance(cast(iot.fn_cal_postion(E.latitude) as numeric), '
                      'cast(iot.fn_cal_postion(E.longitude) as numeric),' +
                       str(latitude) + ',' + str(longitude) + ') <= 5000')
    for i in range(len(data)):
        deviceid = data[i][0]
        type_id = data[i][1]
        latitude = data[i][2]
        longitude = data[i][3]
        ret_list.append({'id': deviceid,
                         'category': type_id,
                         'position': {'lat': cal_position(latitude),
                                      'lng': cal_position(longitude)}})
    return JsonResponse(ret_list, safe=False, status=status.HTTP_200_OK)


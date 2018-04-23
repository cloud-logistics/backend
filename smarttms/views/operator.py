#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from util import logger
from smarttms.models import BoxInfo
from smarttms.models import BoxTypeInfo
from tms.models import SensorData
from util import geo

log = logger.get_logger(__name__)


# 运营方首页数据
@api_view(['GET'])
def home_page(request):
    data = BoxInfo.objects.raw('select D.deviceid, D.type_id, D.temperature,D.longitude,D.latitude,'
                               'boxtypeinfo.temperature_threshold_min,'
                               'boxtypeinfo.temperature_threshold_max,boxtypeinfo.box_type_name '
                               'from (select box_info.deviceid,box_info.type_id,C.temperature,'
                               'C.longitude,C.latitude '
                               'from smarttms_boxinfo box_info '
                               'left join ('
                               'select B.* from (select max(timestamp) as timestamp ,deviceid ' 
                               'from tms_sensordata group by deviceid) A '
                               'left join tms_sensordata B '
                               'on A.timestamp = B.timestamp and A.deviceid = B.deviceid ) C ' 
                               'on C.deviceid=box_info.deviceid '
                               'group by box_info.deviceid,box_info.type_id,C.temperature,C.longitude,C.latitude ) D '
                               'inner join smarttms_boxtypeinfo boxtypeinfo '
                               'on D.type_id = boxtypeinfo.id')
    ret_list = []
    for item in data:
        deviceid = item.deviceid
        type_id = item.type_id
        temperature = float(item.temperature)
        longitude = item.longitude
        latitude = item.latitude
        temperature_threshold_min = float(item.temperature_threshold_min)
        temperature_threshold_max = float(item.temperature_threshold_max)
        box_type_name = item.box_type_name
        status_code = 0
        if temperature < temperature_threshold_min:
            status_code = -1
        if temperature > temperature_threshold_max:
            status_code = 1
        ret_list.append({'deviceid': deviceid, 'type_id': type_id, 'box_type_name': box_type_name,
                         'temperature': temperature, 'status_code': status_code,
                         'temperature_threshold_min': temperature_threshold_min,
                         'temperature_threshold_max': temperature_threshold_max,
                         'longitude': geo.cal_position(longitude),
                         'latitude': geo.cal_position(latitude)})
    return JsonResponse({'data': ret_list}, status=status.HTTP_200_OK, safe=True)


# 运营方云箱状态
@api_view(['GET'])
def box_status(request):
    data = BoxTypeInfo.objects.raw('select count(1) as num,box_type_name,id,used_flag from '
                                   '(select TOTAL.deviceid,TOTAL.box_type_name,TOTAL.id, '
                                   'case when USED.box_id is null then 0 else 1 end as used_flag from '
                                   '(select boxinfo.deviceid,boxtypeinfo.box_type_name,boxtypeinfo.id '
                                   'from smarttms_boxinfo boxinfo '
                                   'inner join smarttms_boxtypeinfo boxtypeinfo '
                                   'on boxinfo.type_id = boxtypeinfo.id) TOTAL '
                                   'left join '
                                   '(select box_id from smarttms_boxorderdetail where state=0 group by box_id) USED '
                                   'on TOTAL.deviceid=USED.box_id) A '
                                   'group by box_type_name,id,used_flag order by used_flag desc')
    ret_data = []
    for item in data:
        num = item.num
        box_type_name = item.box_type_name
        used_flag = item.used_flag
        ret_data.append({'num': num})

    return JsonResponse({'data': ret_data}, status=status.HTTP_200_OK, safe=True)

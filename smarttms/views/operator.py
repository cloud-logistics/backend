#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from util import logger
from smarttms.models import BoxInfo
from smarttms.models import BoxTypeInfo
from smarttms.utils.retcode import *
from util import geo


log = logger.get_logger(__name__)
ERR_MSG = 'server internal error, pls contact admin'


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
        temperature = float((item.temperature, 0)[item.temperature is None])
        longitude = (item.longitude, '0')[item.longitude is None]
        latitude = (item.latitude, '0')[item.latitude is None]
        temperature_threshold_min = float((item.temperature_threshold_min, 0)[item.temperature_threshold_min is None])
        temperature_threshold_max = float((item.temperature_threshold_max, 0)[item.temperature_threshold_max is None])
        box_type_name = item.box_type_name
        status_des = '正常'
        if temperature < temperature_threshold_min:
            status_des = '温度过低'
        if temperature > temperature_threshold_max:
            status_des = '温度过高'
        ret_list.append({'deviceid': deviceid, 'type_id': type_id, 'box_type_name': box_type_name,
                         'temperature': temperature, 'status': status_des,
                         'temperature_threshold_min': temperature_threshold_min,
                         'temperature_threshold_max': temperature_threshold_max,
                         'longitude': geo.cal_position(longitude),
                         'latitude': geo.cal_position(latitude)})
    return JsonResponse(retcode(ret_list, "0000", "Succ"), status=status.HTTP_200_OK, safe=True)


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
    used_box = []
    unused_box = []
    for item in data:
        num = item.num
        box_type_name = item.box_type_name
        id = item.id
        used_flag = item.used_flag
        # 使用中类型的箱子
        if used_flag == 1:
            used_box.append({'box_type_name': box_type_name, 'num': num, 'id': id})
        # 库存
        else:
            unused_box.append({'box_type_name': box_type_name, 'num': num, 'id': id})

    return JsonResponse(retcode({'used_box': used_box, 'unused_box': unused_box}, "0000", "Succ"),
                        status=status.HTTP_200_OK, safe=True)


# 获取箱子类型
@api_view(['GET'])
def box_detail(request):
    try:
        deviceid = request.GET.get("deviceid")
        data = BoxInfo.objects.select_related('type').values_list('type__box_type_name', 'type__id').\
            filter(deviceid=deviceid)
        if len(data) > 0:
            box_type_name = data[0][0]
            type_id = data[0][1]
            return JsonResponse(retcode({'box_type_name': box_type_name, 'type_id': type_id},
                                        "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
        else:
            return JsonResponse(retcode('deviceid not found', "9999", "Fail"),
                                safe=True, status=status.HTTP_400_BAD_REQUEST)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"),
                            safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 扫码用箱
@api_view(['POST'])
def box_rent(request):
    data = request.body
    parameters = json.loads(data)
    pass

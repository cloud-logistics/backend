#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from smarttms.models import BoxInfo, BoxTypeInfo, BoxOrder, BoxOrderDetail, UserAppointment, AppointmentDetail
from smarttms.utils.retcode import *
from util import geo
from django.db import transaction
import uuid
import datetime
import pytz
from django.conf import settings


log = logger.get_logger(__name__)
ERR_MSG = 'server internal error, pls contact admin'
tz = pytz.timezone(settings.TIME_ZONE)



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
    try:
        with transaction.atomic():
            box_order_id = str(uuid.uuid1())
            appointment_id = parameters['appointment_id']
            appointment = AppointmentDetail.objects.select_related('appointment').\
                filter(appointment__appointment_id=appointment_id)
            if not len(appointment) > 0:
                return JsonResponse(retcode('appointment_id dose not exits', "9999", "Fail"),
                                    safe=True, status=status.HTTP_400_BAD_REQUEST)
            else:
                appointment_days = appointment[0].appointment.appointment_days

            # 记录预约的箱子类型及个数对应关系
            appointment_box_info = {}
            for appointment_detail in appointment:
                appointment_box_info[appointment_detail.box_type_id] = appointment_detail.box_num

            # 取当前时间为箱单开始时间
            order_start_time = datetime.datetime.now(tz=tz)
            # 加上预约天数为箱单结束时间
            delta = datetime.timedelta(days=appointment_days)
            order_end_time = order_start_time + delta
            box_order = BoxOrder(box_order_id=box_order_id,
                                 appointment_id=appointment_id,
                                 order_start_time=order_start_time,
                                 order_end_time=order_end_time,
                                 state=0,
                                 ack_flag=0)

            box_type_list = parameters['data']
            box_order_detail_list = []
            for box_type in box_type_list:
                box_type_id = box_type['box_type_id']
                deviceid_list = box_type['deviceid_list']

                # 计算请求参数中每种类型的箱子有多少个
                box_num = 0
                for deviceid in deviceid_list:
                    # 判断每个id是否存在
                    if not if_box_exits(deviceid):
                        return JsonResponse(retcode("deviceid:" + deviceid + " dose not exit", "9999", "Fail"),
                                            safe=True, status=status.HTTP_400_BAD_REQUEST)
                    if if_box_using(deviceid):
                        return JsonResponse(retcode("deviceid:" + deviceid + " is being used", "9999", "Fail"),
                                            safe=True, status=status.HTTP_400_BAD_REQUEST)

                    box_num = box_num + 1
                    box_order_detail = BoxOrderDetail(order_detail_id=str(uuid.uuid1()),
                                                      order_detail_start_time=order_start_time,
                                                      order_detail_end_time=order_end_time,
                                                      box_order_id=box_order_id,
                                                      box_id=deviceid,
                                                      state=0)
                    box_order_detail_list.append(box_order_detail)
                if appointment_box_info[box_type_id] != box_num:
                    return JsonResponse(retcode("box number error", "9999", "Fail"),
                                        safe=True, status=status.HTTP_400_BAD_REQUEST)

            box_order.save()
            for detail in box_order_detail_list:
                detail.save()
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"),
                            safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(retcode({"box_order_id": box_order_id}, "0000", "Succ"),
                        safe=True, status=status.HTTP_201_CREATED)


# 判断云箱id是否存在
def if_box_exits(deviceid):
    try:
        box = BoxInfo.objects.get(deviceid=deviceid)
        if box is not None:
            return True
    except BoxInfo.DoesNotExist, e:
        log.error(e.message)
        return False


# 判断云箱是否正在被使用
def if_box_using(deviceid):
    data = BoxOrderDetail.objects.filter(box__deviceid=deviceid, state=0)
    return len(data) > 0



# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Max, Min
from tms.models import FishingHistory, OperateHistory, User, SensorData
from tms.utils.retcode import *
from util.db import query_list
import time

log = logger.get_logger(__name__)
ERR_MSG = 'server internal error, pls contact admin'


# 获取订单列表
@api_view(['GET'])
def get_order(request):
    try:
        user_id = request.GET.get("user_id")
        order_status = str(request.GET.get("order_status"))  # 0 在运  1 已完成
        role_name = User.objects.select_related('role').get(user_id=user_id).role.role_name

        condition = ' 1=1 '
        if role_name != 'admin':
            condition = condition + ' and user_id = \'' + user_id + '\' '

        if order_status == '0':
            # 在运
            sql = 'select qr_id from tms_operatehistory where ' + condition + \
                  ' and qr_id not in (select qr_id from tms_operatehistory ' \
                  'where op_type = 3 group by qr_id) group by qr_id'
        else:
            # 已完成
            sql = 'select qr_id from tms_operatehistory where ' + condition + \
                  ' and qr_id in (select qr_id from tms_operatehistory ' \
                  'where op_type = 3 group by qr_id) group by qr_id'
        qr_ids = query_list(sql)
        qr_ids_str = []
        for item in qr_ids:
            qr_ids_str.append(item[0])
        data = FishingHistory.objects.select_related('fish_type').\
            select_related('fishery').select_related('unit').\
            values_list('qr_id', 'weight', 'unit__unit_name', 'fish_type__type_name', 'fishery__fishery_name').\
            filter(qr_id__in=qr_ids_str).order_by('qr_id')
        ret_data = []
        for item in data:
            qr_id = item[0]
            timestamp_data = OperateHistory.objects.values_list('timestamp', 'op_type').\
                filter(qr_id=qr_id).filter(op_type__in=['1', '2', '3']).\
                order_by('op_type')  # 获取捕捞时间 / 装车时间 / 交货时间
            obj_dic = {}
            for obj in timestamp_data:
                obj_dic[obj[1]] = obj[0]

            fishing_timestamp = (str(obj_dic.get(1)) + '000', 'NA')[obj_dic.get(1) is None]
            load_timestamp = (str(obj_dic.get(2)) + '000', 'NA')[obj_dic.get(2) is None]
            delivery_timestamp = (str(obj_dic.get(3)) + '000', 'NA')[obj_dic.get(3) is None]

            weight = item[1]
            unit = item[2]
            type_name = item[3]
            fishery_name = item[4]
            ret_data.append({'qr_id': qr_id, 'weight': weight, 'unit': unit,
                             'type_name': type_name, 'fishery_name': fishery_name,
                             'fishing_timestamp': fishing_timestamp,
                             'load_timestamp': load_timestamp,
                             'delivery_timestamp': delivery_timestamp})
        return JsonResponse(retcode(ret_data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 获取订单详情
@api_view(['GET'])
def order_detail(request):
    try:
        qr_id = request.GET.get("qr_id")
        ret_data = {}
        op_list = []

        # 获取订单的基本信息
        order_data = FishingHistory.objects.select_related('fish_type').select_related('fishery').select_related('unit').\
            values_list('fish_type__type_name', 'fishery__fishery_name', 'unit__unit_name', 'weight').filter(qr_id=qr_id)

        if len(order_data) > 0:
            ret_data['fish_type_name'] = order_data[0][0]
            ret_data['fishery_name'] = order_data[0][1]
            ret_data['unit_name'] = order_data[0][2]
            ret_data['weight'] = order_data[0][3]

        # 获取订单的操作流水
        op_history_data = OperateHistory.objects.select_related('user').\
            values_list('timestamp', 'user__user_name', 'op_type').\
            filter(qr_id=qr_id).order_by('timestamp')
        for item in op_history_data:
            timestamp = item[0]
            user_name = item[1]
            op_type_flag = item[2]
            if op_type_flag == 1:
                op_type = '捕捞'
            elif op_type_flag == 2:
                op_type = '装车'
            elif op_type_flag == 3:
                op_type = '商家收货'
            else:
                op_type = '其他'

            op_list.append({'timestamp': timestamp, 'user_name': user_name,
                            'op_type': op_type, 'op_type_flag': op_type_flag})
        ret_data['op_list'] = op_list

        return JsonResponse(retcode(ret_data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 获取指标历史曲线
@api_view(['GET'])
def indicator_history(request):
    try:
        qr_id = request.GET.get("qr_id")
        indicator_type = request.GET.get('indicator_type')
        # 默认显示20个点
        points = 20
        ret_list = []

        if indicator_type in ('salinity', 'ph', 'dissolved_oxygen', 'temperature'):
            indicator = indicator_type
        else:
            indicator = 'salinity'

        # 获取订单起始时间和结束时间
        min_time_data = OperateHistory.objects.filter(qr_id=qr_id).aggregate(Min('timestamp'))
        max_time_data = OperateHistory.objects.filter(qr_id=qr_id).aggregate(Max('timestamp'))
        start_time = min_time_data['timestamp__min']
        end_time = max_time_data['timestamp__max']

        # 获取订单对应的deviceid
        deviceid_data = FishingHistory.objects.select_related('flume').values_list('flume__deviceid').filter(qr_id=qr_id)
        if len(deviceid_data) > 0:
            deviceid = deviceid_data[0][0]
        else:
            deviceid = ''

        data_list = query_list('SELECT * FROM fn_indicator_history(' + str(start_time) + ',' +
                               str(end_time) + ',' + str(points) + ',\'' +
                               str(indicator) + '\',\'' + str(deviceid) + '\') AS (value DECIMAL, x INTEGER)')
        # 根据查询到到数据，由list转为dict
        time_map = {}
        for item in data_list:
            time_map[item[1]] = item[0]

        # 构造最终返回list
        for i in range(points):
            value_dict = {}
            step = ((end_time - start_time) / points)

            x1 = time.strftime('%Y-%m-%d %H:%M', time.localtime(i * step + start_time))
            x2 = time.strftime('%Y-%m-%d %H:%M', time.localtime((i + 1) * step + start_time))
            if i == points - 1:
                x2 = time.strftime('%Y-%m-%d %H:%M', time.localtime(end_time))
            value_dict['time'] = x1 + '~' + x2
            if i in time_map.keys():
                value_dict['value'] = time_map.get(i)
            else:
                value_dict['value'] = 'NA'
            ret_list.append(value_dict)
        return JsonResponse(retcode(ret_list, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 获取订单数量统计
@api_view(['GET'])
def order_statistic(request):
    try:
        user_id = request.GET.get("user_id")
        role_name = User.objects.select_related('role').get(user_id=user_id).role.role_name
        condition = ' 1=1 '
        if role_name != 'admin':
            condition = condition + ' and user_id = \'' + user_id + '\' '

        # 在运
        sql_ongoing = 'select count(1) FROM (select DISTINCT(qr_id) ' \
                      ' from tms_operatehistory where ' + condition + \
                      ' and qr_id not in (select qr_id from tms_operatehistory ' \
                      'where op_type = 3 group by qr_id) group by qr_id) A'
        data_ongoing = query_list(sql_ongoing)

        # 已完成
        sql_done = 'select count(1) FROM (select DISTINCT(qr_id) ' \
                   ' from tms_operatehistory where ' + condition + \
                   ' and qr_id in (select qr_id from tms_operatehistory ' \
                   'where op_type = 3 group by qr_id) group by qr_id) A'
        data_done = query_list(sql_done)
        ret_data = {}
        ret_data['notice_num'] = 0
        if len(data_ongoing) > 0:
            ret_data['ongoing_num'] = data_ongoing[0][0]
        else:
            ret_data['ongoing_num'] = 0
        if len(data_done) > 0:
            ret_data['done_num'] = data_done[0][0]
        else:
            ret_data['done_num'] = 0
        return JsonResponse(retcode(ret_data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 获取在运虾盒温度等指标当前值
@api_view(['GET'])
def current_status(request):
    try:
        qr_id = request.GET.get("qr_id")
        # 获取订单对应的deviceid
        deviceid_data = FishingHistory.objects.select_related('flume').values_list('flume__deviceid').filter(qr_id=qr_id)
        if len(deviceid_data) > 0:
            deviceid = deviceid_data[0][0]
        else:
            deviceid = ''
        data = SensorData.objects.filter(deviceid=deviceid).order_by('-timestamp').first()
        if data is not None:
            temperature = data.temperature
            ph = data.ph
            salinity = data.salinity
            dissolved_oxygen = data.dissolved_oxygen
        else:
            temperature = 'NA'
            ph = 'NA'
            salinity = 'NA'
            dissolved_oxygen = 'NA'
        ret_data = {'temperature': temperature,
                    'ph': ph,
                    'salinity': salinity,
                    'dissolved_oxygen': dissolved_oxygen}
        return JsonResponse(retcode(ret_data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 获取在运/已完成虾盒gps轨迹
@api_view(['GET'])
def history_path(request):
    try:
        qr_id = request.GET.get("qr_id")
        ret_list = []

        FishingHistory.objects.filter(qr_id=qr_id)

        # 获取订单起始时间和结束时间
        min_time_data = OperateHistory.objects.filter(qr_id=qr_id).aggregate(Min('timestamp'))
        max_time_data = OperateHistory.objects.filter(qr_id=qr_id).aggregate(Max('timestamp'))
        start_time = min_time_data['timestamp__min']
        end_time = max_time_data['timestamp__max']

        # 获取订单对应的deviceid
        deviceid_data = FishingHistory.objects.select_related('flume').values_list('flume__deviceid').filter(qr_id=qr_id)
        if len(deviceid_data) > 0:
            deviceid = deviceid_data[0][0]
        else:
            deviceid = ''

        return JsonResponse(retcode(ret_list, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
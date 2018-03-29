# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Max, Min
from tms.models import FishingHistory, OperateHistory, User, SensorData, FishType, NotifyMessage
from tms.serializers import SensorPathDataSerializer, FishTypeSerializer
from tms.utils.retcode import *
from util.db import query_list
import time
from math import ceil

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
        ret_data['notice_num'] = NotifyMessage.objects.filter(user_id=user_id, read_flag='N').count()

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
        order_data = FishingHistory.objects.select_related('fishery').\
            values_list('fishery__longitude', 'fishery__latitude', 'order_status').filter(qr_id=qr_id)
        if len(order_data) > 0:
            fishery_longitude = order_data[0][0]
            fishery_latitude = order_data[0][1]
            order_status = order_data[0][2]
        else:
            return JsonResponse(retcode('qr_id not found', "9999", "Fail"), safe=True,
                                status=status.HTTP_400_BAD_REQUEST)

        min_time_data = OperateHistory.objects.filter(qr_id=qr_id).aggregate(Min('timestamp'))
        start_time = min_time_data['timestamp__min']
        fishery_point = []
        fishery_point.append({'timestamp': start_time, 'longitude': fishery_longitude, 'latitude': fishery_latitude})

        # 已经装车运输，水箱的gps信息可看作虾盒的pgs信息
        if order_status != '0':
            # 获取订单起始时间和结束时间
            max_time_data = OperateHistory.objects.filter(qr_id=qr_id).aggregate(Max('timestamp'))
            end_time = max_time_data['timestamp__max']
            # 获取订单对应的deviceid
            data = FishingHistory.objects.select_related('flume').select_related('fishery').\
                values_list('flume__deviceid', 'fishery__longitude', 'fishery__latitude', 'order_status').\
                filter(qr_id=qr_id)
            if len(data) > 0:
                deviceid = data[0][0]
            else:
                deviceid = ''
            locations = SensorData.objects.filter(deviceid=deviceid,
                                                  timestamp__gt=start_time, timestamp__lte=end_time)
            total_num = len(locations)
            if total_num > 0:
                span_num = 20
                step = int(ceil(total_num / float(span_num)))
                locations = locations[::step]
            locations_ser = SensorPathDataSerializer(locations, many=True)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(retcode(fishery_point + list(locations_ser.data), "0000", "Succ"),
                            safe=True, status=status.HTTP_200_OK)


# 获取阈值列表
@api_view(['GET'])
def threshold_list(request):
    fish_type_data = FishType.objects.all().order_by('type_name')
    ret_data = FishTypeSerializer(fish_type_data, many=True)
    return JsonResponse(retcode(ret_data.data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)


# 添加阈值
@api_view(['POST'])
def add_threshold(request):
    try:
        data = request.body
        parameters = json.loads(data)
        required_parameters = ['type_name',
                               'salinity_min', 'salinity_max',
                               'ph_min', 'ph_max',
                               'dissolved_oxygen_min', 'dissolved_oxygen_max',
                               'temperature_min', 'temperature_max']
        for key in required_parameters:
            if not parameter_is_valid(data, key):
                return JsonResponse(retcode(key + ' is required', "9999", "Fail"), safe=True,
                                    status=status.HTTP_400_BAD_REQUEST)
        exists_data = FishType.objects.filter(type_name=parameters['type_name'])
        if len(exists_data) > 0:
            return JsonResponse(
                retcode('type_name [' + parameters['type_name'] + '] already exists', "9999", "Fail"), safe=True,
                status=status.HTTP_400_BAD_REQUEST)
        d = FishType(type_name=parameters['type_name'],
                     salinity_min=parameters['salinity_min'], salinity_max=parameters['salinity_max'],
                     ph_min=parameters['ph_min'], ph_max=parameters['ph_max'],
                     dissolved_oxygen_min=parameters['dissolved_oxygen_min'],
                     dissolved_oxygen_max=parameters['dissolved_oxygen_max'],
                     temperature_min=parameters['temperature_min'], temperature_max=parameters['temperature_max'])
        d.save()
        return JsonResponse(retcode('save fish type threshold successfully', "0000", "Succ"),
                            safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"),
                            safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 修改阈值
@api_view(['POST'])
def alter_threshold(request, type_id):
    try:
        data = request.body
        parameters = json.loads(data)
        required_parameters = ['salinity_min', 'salinity_max',
                               'ph_min', 'ph_max',
                               'dissolved_oxygen_min', 'dissolved_oxygen_max',
                               'temperature_min', 'temperature_max']
        for key in required_parameters:
            if not parameter_is_valid(data, key):
                return JsonResponse(retcode(key + ' is required', "9999", "Fail"), safe=True,
                                    status=status.HTTP_400_BAD_REQUEST)
        fish_type = FishType.objects.get(type_id=type_id)
        fish_type.salinity_min = parameters['salinity_min']
        fish_type.salinity_max = parameters['salinity_max']
        fish_type.ph_min = parameters['ph_min']
        fish_type.ph_max = parameters['ph_max']
        fish_type.dissolved_oxygen_min = parameters['dissolved_oxygen_min']
        fish_type.dissolved_oxygen_max = parameters['dissolved_oxygen_max']
        fish_type.temperature_min = parameters['temperature_min']
        fish_type.temperature_max = parameters['temperature_max']
        fish_type.save()
        return JsonResponse(retcode('modify fish type threshold successfully', "0000", "Succ"),
                            safe=True, status=status.HTTP_200_OK)
    except FishType.DoesNotExist:
        return JsonResponse(retcode('Fish Type dose not exists', "9999", "Fail"),
                            safe=True, status=status.HTTP_400_BAD_REQUEST)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"),
                            safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 删除阈值
@api_view(['DELETE'])
def del_threshold(request, type_id):
    try:
        data = FishingHistory.objects.select_related('fish_type').filter(fish_type__type_id=type_id)
        if len(data) > 0:
            return JsonResponse(retcode('Fish Type is being used, can\'t be deleted', "9999", "Fail"),
                                safe=True, status=status.HTTP_400_BAD_REQUEST)
        else:
            FishType.objects.get(type_id=type_id).delete()
            return JsonResponse(retcode('delete fish type threshold successfully', "0000", "Succ"),
                                safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(repr(e))
        return JsonResponse(retcode(ERR_MSG, "9999", "Fail"),
                            safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 判断参数是否存在，是否合法
def parameter_is_valid(data, parameter_name):
    try:
        parameters = json.loads(data)
        return parameter_name in parameters and '' != to_str(parameters[parameter_name])
    except Exception, e:
        log.error(repr(e))
        return False


# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


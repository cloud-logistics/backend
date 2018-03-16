# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Max, Min
from tms.models import FishingHistory, OperateHistory
from tms.utils.retcode import *
from util.db import query_list

log = logger.get_logger(__name__)


# 获取订单列表
@api_view(['GET'])
def get_order(request):
    try:
        user_id = request.GET.get("user_id")
        order_status = request.GET.get("order_status")  # 1 已经捕捞  2 已经装车  3 已经交付商家
        data = FishingHistory.objects.raw('select fishinghistory.qr_id,weight,unit.unit_name,"user".user_name '
                                          'as fishman_name,fishtype.type_name,fishery.fishery_name '
                                          'from tms_fishinghistory fishinghistory '
                                          'inner join tms_operatehistory operatehistory '
                                          'on fishinghistory.qr_id = operatehistory.qr_id '
                                          ' and operatehistory.op_type = ' + order_status +
                                          ' inner join tms_unit unit on fishinghistory.unit_id = unit.unit_id '
                                          'inner join tms_user "user" on operatehistory.user_id = "user".user_id '
                                          'inner join tms_fishtype fishtype on fishtype.type_id = fishinghistory.fish_type_id '    
                                          'inner join tms_fishery fishery on fishery.fishery_id = fishinghistory.fishery_id '
                                          'and operatehistory.user_id = \'' + user_id + '\'')
        ret_data = []
        for item in data:
            qr_id = item.qr_id
            weight = item.weight
            unit = item.unit_name
            type_name = item.type_name
            fishery_name = item.fishery_name
            ret_data.append({'qr_id': qr_id, 'weight': weight, 'unit': unit,
                             'type_name': type_name, 'fishery_name': fishery_name})
        return JsonResponse(retcode(ret_data, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        err_msg = 'server internal error, pls contact admin'
        return JsonResponse(retcode(err_msg, "9999", "Fail"), safe=True,
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
        err_msg = 'server internal error, pls contact admin'
        return JsonResponse(retcode(err_msg, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 获取指标历史曲线
@api_view(['GET'])
def indicator_history(request):
    try:
        qr_id = request.GET.get("qr_id")
        indicator_type = request.GET.get('indicator_type')

        if indicator_type in ('salinity', 'ph', 'dissolved_oxygen'):
            indicator = indicator_type
        else:
            indicator = 'salinity'

        min_time_data = OperateHistory.objects.annotate(Min('timestamp')).filter(qr_id=qr_id)
        max_time_data = OperateHistory.objects.annotate(Max('timestamp')).filter(qr_id=qr_id)

        start_time = min_time_data[0].timestamp
        end_time = max_time_data[0].timestamp

        data_list = query_list('SELECT * FROM fn_indicator_history(' + str(start_time) + ',' +
                               str(end_time) + ',\'' + indicator + '\',\'' + id + '\') AS (value DECIMAL, hour INTEGER)')

        return JsonResponse(retcode(data_list, "0000", "Succ"), safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        err_msg = 'server internal error, pls contact admin'
        return JsonResponse(retcode(err_msg, "9999", "Fail"), safe=True,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



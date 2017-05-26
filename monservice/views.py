#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from util.db import query_list
from util import logger

# Create your views here.

log = logger.get_logger('monservice.view.py')
file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'mock_data.json'
NOT_APPLICABLE = 'NA'
ZERO = 0

@csrf_exempt
def containers_overview(request):
    try:
        with open(str(file_path)) as f:
            load_dict = json.load(f)
        return JsonResponse(load_dict, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('containers_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False ,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def satellites_overview(request):
    try:
        with open(str(file_path)) as f:
            load_dict = json.load(f)
        return JsonResponse(load_dict, safe=False, status=status.HTTP_200_OK)
    except Exception, e:
        log.error('satellites_overview response error, msg: ' + e.__str__())
        return JsonResponse('', safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def realtime_message(request):
    pass


@csrf_exempt
def realtime_position(request):
    id = 'ESP32_AI_001'
    data = query_list('select box_info.deviceid, carrier_info.carrier_name, site_info_src.location, site_info_dst.location '
                      'from iot.box_info box_info left join ' 
                      'iot.box_order_relation relation on box_info.deviceid = relation.deviceid ' 
                      'left join iot.order_info order_info on order_info.trackid = relation.trackid ' 
                      'left join iot.carrier_info carrier_info on carrier_info.id = box_info.carrierid '
                      'left join iot.site_info site_info_src on site_info_src.id = order_info.srcid '
                      'left join iot.site_info site_info_dst on site_info_dst.id = order_info.dstid '
                      'where box_info.deviceid = \'' + id + '\' ' 
                      ' group by box_info.deviceid,carrier_info.carrier_name, site_info_src.location, site_info_dst.location')

    if len(data) > 0:
        clientid = to_str(data[0][0])
        carrier = to_str(data[0][1])
        origination = to_str(data[0][2])
        destination = to_str(data[0][3])
    else:
        clientid = NOT_APPLICABLE
        carrier = NOT_APPLICABLE
        origination = NOT_APPLICABLE
        destination = NOT_APPLICABLE

    ori_data = query_list('select latitude, longitude from iot.site_info where location = \'' + origination + '\'')
    dst_data = query_list('select latitude, longitude from iot.site_info where location = \'' + destination + '\'')
    if len(ori_data) > 0:
        ori_latitude = float(to_str(ori_data[0][0]))
        ori_longitude = float(to_str(ori_data[0][1]))
    else:
        ori_latitude = ZERO
        ori_longitude = ZERO

    if len(dst_data) > 0:
        dst_latitude = float(to_str(dst_data[0][0]))
        dst_longitude = float(to_str(dst_data[0][1]))
    else:
        dst_latitude = ZERO
        dst_longitude = ZERO

    cur_data = query_list('select latitude,longitude from iot.sensor_data '
                          'where deviceid = \'' + clientid + '\' order by timestamp desc limit 1')
    if len(cur_data) > 0:
        cur_latitude = cal_position(cur_data[0][0])
        cur_longitude = cal_position(cur_data[0][1])
    else:
        cur_latitude = ZERO
        cur_longitude = ZERO

    ret_data = {'containerInstantInfo':
                {'containerInfo': {'containerId': clientid, 'carrier': carrier},
                 'startPosition': {'lng': ori_longitude, 'lat': ori_latitude},
                 'currentPosition': {'lng': cur_longitude, 'lat': cur_latitude},
                 'endPosition': {'lng': dst_longitude, 'lat': dst_latitude}}}

    return JsonResponse(ret_data, safe=False, status=status.HTTP_200_OK)


@csrf_exempt
def history_path(request):
    pass


@csrf_exempt
def alarm_monitor(request):
    pass


@csrf_exempt
def basic_info(request):
    data = query_list('select deviceid, iot.box_type_info.box_type_name, produce_area, manufacturer, ' 
                      'iot.carrier_info.carrier_name, date_of_production ' 
                      'from iot.box_info '
                      'inner join iot.box_type_info on iot.box_info.type = iot.box_type_info.id '
                      'inner join iot.carrier_info on iot.box_info.carrierid = iot.carrier_info.id')
    ret_list = []
    for item in data:
        dicitem = {}
        dicitem['containerId'] = to_str(item[0])
        dicitem['containerType'] = to_str(item[1])
        dicitem['factoryLocation'] = to_str(item[2])
        dicitem['factory'] = to_str(item[3])
        dicitem['carrier'] = to_str(item[4])
        dicitem['factoryDate'] = to_str(item[5])
        ret_list.append(dicitem)

    ret_dic = {'basicInfo': ret_list}

    return JsonResponse(ret_dic, safe=False, status=status.HTTP_200_OK)


@csrf_exempt
def history_message(request):
    param = request.body
    container_dic_list = []
    final_response = {}
    if param:
        try:
            param_dic = json.loads(param)
            if param_dic['containerId'] and param_dic['startTime'] and param_dic['endTime']:
                request_starttime = param_dic['startTime']
                request_endtime = param_dic['endTime']
                query_template = '''select srcid, dstid, starttime, endtime
                        from iot.order_info where iot.order_info.trackid
                        in (select trackid from iot.box_order_relation
                        where iot.box_order_relation.deviceid = '%s')''' % param_dic['containerId']
                order_info_query_list = query_list(query_template)
                site_info_query_list = query_list('select id, latitude, longitude from iot.site_info')
                site_info_dic = {}
                '''
                site info dic
                dic ['id'] = {'lat':12, 'lng':120}
                '''
                for item in site_info_query_list:
                    gpsdic = {}
                    gpsdic['lat'] = item[1]
                    gpsdic['lng'] = item[2]
                    site_info_dic[item[0]] = gpsdic
                # contract final response
                for item in order_info_query_list:
                    if int(request_starttime) <= int(item[2]) and int(request_endtime) >= int(item[3]):
                        start_dic = {}
                        start_dic['time'] = item[2]
                        if item[0] in site_info_dic.keys():
                            start_dic['position'] = site_info_dic[item[0]]
                        end_dic = {}
                        end_dic['time'] = item[3]
                        if item[1] in site_info_dic.keys():
                            end_dic['position'] = site_info_dic[item[1]]
                        container_dic = {}
                        container_dic['containerId'] = param_dic['containerId']
                        container_dic['start'] = start_dic
                        container_dic['end'] = end_dic
                        container_dic_list.append(container_dic)
                final_response['containerhistory'] = container_dic_list
                log.debug(final_response)
        except Exception, e:
            log.error(e)
        finally:
            return JsonResponse(final_response, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse(final_response, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@csrf_exempt
def status_summary(request):
    pass


def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


# 将传感器数据的经度或纬度转换为小数点形式，Longitude: 116296046, //dddmmmmmm   Latitude: 39583032,  //ddmmmmmm
def cal_position(value):
    hour = value[:-6]
    minute = value[len(hour):len(value)]

    return float(hour + '.' + minute)


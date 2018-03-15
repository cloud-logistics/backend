# -*- coding: utf-8 -*-


from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse
import time
from util import logger
from tms.models import SensorData

log = logger.get_logger(__name__)


# 接收传感器数据
@api_view(['POST'])
def receive_data(request):
    log.debug('tms receive data' + request.body)

    token = request.META.get('HTTP_TOKEN')
    if token is None or token != 'a921a69a33ae461396167d112b813d90':
        return JsonResponse(organize_result("False", "999999", "Unauthorized", {}),
                            status=status.HTTP_401_UNAUTHORIZED, safe=True)
    try:
        parameters = JSONParser().parse(request)
        sensor_data = SensorData(timestamp=parameters['timestamp'],
                                 intimestamp=int(time.time()),
                                 deviceid=parameters['deviceid'],
                                 temperature=parameters['temperature'],
                                 longitude=parameters['longitude'],
                                 latitude=parameters['latitude'],
                                 salinity=parameters['salinity'],
                                 ph=parameters['ph'],
                                 dissolved_oxygen=parameters['dissolved_oxygen'],
                                 chemical_oxygen_consumption=parameters['chemical_oxygen_consumption'],
                                 transparency=parameters['transparency'],
                                 aqua=parameters['aqua'],
                                 nutrient_salt_of_water=parameters['nutrient_salt_of_water'],
                                 anaerobion=parameters['anaerobion'])
        sensor_data.save()
        return JsonResponse(organize_result("True", "000000", "OK", '{}'), status=status.HTTP_200_OK, safe=True)
    except Exception, e:
        log.error(e.message)
        return JsonResponse(organize_result("False", "999999", e.message, '{}'),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=True)


# 构造返回数据结构
def organize_result(result, code, msg, t):
    return {"result": result, "code": code, "msg": msg, "t": t}
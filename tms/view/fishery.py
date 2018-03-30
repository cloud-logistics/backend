#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Flow of tms'''


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from tms.models import Fishery
import json
from util import logger


log = logger.get_logger(__name__)


# 增加渔场
@csrf_exempt
@api_view(['POST'])
def create_fishery(request):
    try:
        data = json.loads(request.body)
        fishery_name = data['name']
        longitude = data['longitude']
        latitude = data['latitude']

        fishery_list = Fishery.objects.filter(fishery_name= fishery_name)
        if len(fishery_list) > 0:
            response_msg = {'status': 'ERROR', 'msg': u'渔场名称已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        fishery = Fishery(fishery_name=fishery_name, longitude=longitude, latitude=latitude)
        fishery.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'save fishery success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 修改渔场
@csrf_exempt
@api_view(['PUT'])
def update_fishery(request, fishery_id):
    try:
        data = json.loads(request.body)
        fishery_name = data['name']
        longitude = data['longitude']
        latitude = data['latitude']

        fishery_list = Fishery.objects.filter(fishery_name= fishery_name).exclude(fishery_id=fishery_id)
        if len(fishery_list) > 0:
            response_msg = {'status': 'ERROR', 'msg': u'渔场名称已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        fishery = Fishery.objects.get(fishery_id=fishery_id)
        fishery.fishery_name = fishery_name
        fishery.longitude = longitude
        fishery.latitude = latitude
        fishery.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'update fishery success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 删除渔场
@csrf_exempt
@api_view(['DELETE'])
def delete_fishery(request, fishery_id):
    try:

        Fishery.objects.get(fishery_id=fishery_id).delete()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status':'OK', 'msg': 'delete fishery success.'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)
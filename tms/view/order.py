# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse
from tms.models import FishingHistory, OperateHistory
from util import logger


log = logger.get_logger(__name__)


# 在运订单列表
@api_view(['GET'])
def ongoing_order(request):
    user_id = request.GET.get("user_id")
    data = FishingHistory.objects.raw('select fishinghistory."QR_id",weight,unit.unit_name,"user".user_name '
                                      'as fishman_name '
                                      'from iot.tms_fishinghistory fishinghistory '
                                      'inner join iot.tms_operatehistory operatehistory '
                                      'on fishinghistory."QR_id" = operatehistory."QR_id" '
                                      'and fishinghistory.order_status = 1 and operatehistory.operate_type = 1 '
                                      'inner join iot.tms_unit unit on fishinghistory.unit_id = unit.unit_id '
                                      'inner join iot.tms_user "user" on operatehistory.user_id = "user".user_id '
                                      'and operatehistory.user_id = \'' + user_id + '\'')
    
    

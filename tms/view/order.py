# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse
from util import logger


log = logger.get_logger(__name__)


# 在运订单列表
@api_view(['GET'])
def ongoing_order(request):
    QR_id = request.GET.get("QR_id")



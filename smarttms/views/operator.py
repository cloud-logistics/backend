#! /usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from util import logger

log = logger.get_logger(__name__)


# 接收传感器数据
@api_view(['GET'])
def home_page(request):
    return JsonResponse({'test'}, status=status.HTTP_401_UNAUTHORIZED, safe=True)


#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# Create your views here.
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logger
from db import save_to_db

# logging
log = logger.get_logger('view.py')
RESULT_200_OK = {'result': 'ok', 'code': '200'}
RESULT_400_BAD_REQUEST = {'result': 'bad request', 'code': '400'}


@csrf_exempt
def input_data(request):

    if request.method == 'POST' or request.method == 'PUT':
        try:
            log.debug('receive request body:' + request.body)
            save_to_db(request.body)
            log.info('insert data to database successfully')
            return JsonResponse(RESULT_200_OK, status=status.HTTP_200_OK)
        except Exception, e:
            log.error('save to db error, msg: ' + e.__str__())
            return JsonResponse(RESULT_400_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)
    else:
        log.error('bad request method. please use POST/PUT.')
        return JsonResponse(RESULT_400_BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)


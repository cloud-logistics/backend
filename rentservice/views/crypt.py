#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rentservice.utils import cryptoutils
from rentservice.utils.retcode import *


@csrf_exempt
@api_view(['POST'])
def ble_encrypt(request):
    data = JSONParser().parse(request)
    try:
        enc_data = data['data']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入待加密的数据"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    aes = cryptoutils.aescrypt()
    return JsonResponse(retcode({"enc_data": str.upper(aes.encrypt(enc_data))}, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def ble_decrypt(request):
    data = JSONParser().parse(request)
    try:
        dec_data = data['data']
    except Exception:
        return JsonResponse(retcode({}, "9999", "请输入待解密的数据"), safe=True, status=status.HTTP_400_BAD_REQUEST)
    aes = cryptoutils.aescrypt()
    return JsonResponse(retcode({"dec_data": str.upper(aes.decrypt(dec_data))}, "0000", "Success"), safe=True,
                        status=status.HTTP_200_OK)

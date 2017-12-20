#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from monservice.serializers import SiteFullInfoSerializer, BoxFullInfoSerializer
import json
from monservice.models import SiteInfo, City, Province, Nation, BoxTypeInfo, BoxInfo, SiteBoxStock, SiteDispatch
from util import logger
from rest_framework.settings import api_settings
from monservice.models import SiteHistory
import time
import datetime
from django.db import transaction
from util.sid import generate_sid
import httplib
import urllib2
import urllib


log = logger.get_logger('monservice.site.py')

# 将unicode转换utf-8编码
def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('UTF-8')
    else:
        value = unicode_or_str
    return value


# 新增仓库
@csrf_exempt
@api_view(['POST'])
def add_site(request):
    try:
        data = json.loads(request.body)
        location = to_str(data['location'])             # 仓库名称
        name = data['name']  # 名称
        telephone = data['telephone']   # 联系方式

        if name == '':
            response_msg = {'status': 'ERROR', 'msg': u'仓库名称不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        sites = SiteInfo.objects.filter(name=name)
        if len(sites) > 0:
            response_msg = {'status': 'ERROR', 'msg': u'仓库名称已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        if location == '':
            response_msg = {'status': 'ERROR', 'msg': u'位置不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        longitude = to_str(data['longitude'])          # 经度
        if longitude == '':
            response_msg = {'status': 'ERROR', 'msg': u'经度不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)
        latitude = to_str(data['latitude'])             # 纬度

        if latitude == '':
            response_msg = {'status': 'ERROR', 'msg': u'纬度不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        if telephone == '':
            response_msg = {'status': 'ERROR', 'msg': u'联系方式不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        sites = SiteInfo.objects.filter(telephone=telephone)
        if len(sites) > 0:
            response_msg = {'status': 'ERROR', 'msg': u'联系方式已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        volume = data['volume']                         # 仓库箱子容量
        city_id = data['city_id']                       # 城市
        province_id = data['province_id']               # 省
        nation_id = data['nation_id']                   # 国家

        city = City.objects.get(id=city_id)
        province = Province.objects.get(province_id=province_id)
        nation = Nation.objects.get(nation_id=nation_id)

        site_code = generate_sid(city.city_name)        # 仓库代码

        site = SiteInfo(name= name, location=location, latitude=latitude, longitude=longitude, site_code=site_code,
                        city= city, province=province, nation=nation, volume=volume, telephone=telephone)
        site.save()

        initialize_box_num(site.id)

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': u'录入仓库失败！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'录入仓库成功！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 删除仓库
@csrf_exempt
@api_view(['DELETE'])
def delete_site(request, id):
    try:
        # 如果仓库有箱子，则提示不能删除仓库
        boxes = BoxInfo.objects.filter(siteinfo_id=id)
        if len(boxes) > 0:
            response_msg = {'status': 'ERROR', 'msg': u'仓库内还有箱子，不能删除该仓库！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            SiteInfo.objects.get(id=id).delete()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'删除仓库成功！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 修改仓库
@csrf_exempt
@api_view(['PUT'])
def modify_site(request, id):
    try:
        data = json.loads(request.body)

        site = SiteInfo.objects.get(id=id)
        name = data['name']  # 名称
        if name == '':
            response_msg = {'status': 'ERROR', 'msg': u'仓库名称不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        sites = SiteInfo.objects.filter(name=name).exclude(id=id)
        if sites.count() > 0:
            response_msg = {'status': 'ERROR', 'msg': u'仓库名称已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        telephone = str(data['telephone'])
        if telephone == '':
            response_msg = {'status': 'ERROR', 'msg': u'联系方式不能为空！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        sites = SiteInfo.objects.filter(telephone=telephone).exclude(id=id)
        if sites.count() > 0:
            response_msg = {'status': 'ERROR', 'msg': u'联系方式已存在！'}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_400_BAD_REQUEST)

        site.location = to_str(data['location'])  # 仓库位置
        site.longitude = to_str(data['longitude'])  # 经度
        site.latitude = to_str(data['latitude'])  # 纬度
        site.site_code = to_str(data['site_code'])  # 仓库代码
        site.volume = data['volume']  # 仓库箱子容量
        site.name = name
        site.telephone = telephone

        city_id = data['city_id']  # 城市
        province_id = data['province_id']  # 省
        nation_id = data['nation_id']  # 国家
        city = City.objects.get(id=city_id)
        province = Province.objects.get(province_id=province_id)
        nation = Nation.objects.get(nation_id=nation_id)
        site.city = city
        site.province = province
        site.nation = nation
        site.save()

    except Exception, e:
        log.error(e.message)
        response_msg = {'status': 'ERROR', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': u'修改仓库成功！'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 获取全部仓库信息
@csrf_exempt
@api_view(['GET'])
def get_sites(request):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        offset = request.GET.get('offset')
        sites = SiteInfo.objects.all().order_by('id')
        page = paginator.paginate_queryset(sites, request)
        ret_ser = SiteFullInfoSerializer(page, many=True)
        if offset is None:
            return JsonResponse({'data': {'results': SiteFullInfoSerializer(sites, many=True).data}},
                                safe=True, status=status.HTTP_200_OK)
    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', u'查询全部仓库成功！')


# 根据仓库ID获取仓库内的云箱
@csrf_exempt
@api_view(['GET'])
def get_site_boxes(request, id):
    try:
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        boxes = BoxInfo.objects.filter(siteinfo_id=id).order_by('deviceid')
        page = paginator.paginate_queryset(boxes, request)
        ret_ser = BoxFullInfoSerializer(page, many=True)

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return paginator.get_paginated_response(ret_ser.data, 'OK', 'query sites box success')


# 仓库箱子热力图
@csrf_exempt
@api_view(['GET'])
def get_box_by_allsite(request):

    try:
        site_list = SiteInfo.objects.all().order_by('id')
        res_site = []
        for item in site_list:
            stocks = SiteBoxStock.objects.filter(site=item)
            site_box_num = 0
            for stock in stocks:
                site_box_num += stock.ava_num

            res_site.append(
                {'id': item.id, 'location': item.location, 'latitude': item.latitude, 'longitude': item.longitude,
                 'site_code': item.site_code, 'box_num': site_box_num})

    except Exception, e:
        log.error(e.message)
        response_msg = {'code': 'ERROR', 'message': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        response_msg = {'sites': res_site, 'status': 'OK', 'msg': 'query distribution success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 获取某个仓库箱子进出流水
@csrf_exempt
@api_view(['GET'])
def get_site_stream(request, id):
    try:
        ret_data = []
        data = SiteHistory.objects.filter(site_id=id)
        for record in data:
            ts = record.timestamp
            box_id = record.box_id
            type = record.op_type
            timestr = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            # 操作类型：1表示入仓，0表示出仓
            if type == 1:
                typestr = '入库'
            else:
                typestr = '出库'

            ret_data.append({'timestamp': timestr, 'box_id': box_id, 'type': typestr})
        resp = {'site_id': str(id), 'siteHistory': ret_data}
    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(resp, safe=True, status=status.HTTP_200_OK)


# 箱子入库、出库接口
@csrf_exempt
@api_view(['POST'])
def box_inout(request):
    try:
        data = json.loads(request.body)
        site_id = str(data['site_id'])  # 仓库id
        boxes = data['boxes']  # 箱子数组
        ts = str(time.time())[0:10]
        box_type_set = set()
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])     # 箱子id
                type = str(box['type'])         # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site_id=site_id, box_id=box_id, op_type=type)
                history.save()

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                stock = SiteBoxStock.objects.get(site_id=site_id, box_type=box.type)
                if type == '1':
                    box.siteinfo_id = site_id
                else:
                    if stock.ava_num == 0:
                        return
                    box.siteinfo = None
                box_type_set.add(box.type)
                box.save()

        check_stock_ava_num(site_id, box_type_set)

    except Exception, e:
        log.error(e.message)
        response_msg = {'msg': e.message, 'status': 'ERROR'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'status': 'OK', 'msg': 'post box inout success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 租赁平台：箱子进出仓库
def enter_leave_site(data):
    try:
        site_id = str(data['site_id'])  # 仓库id
        boxes = data['boxes']  # 箱子数组
        ts = str(time.time())[0:10]
        box_type_set = set()
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])  # 箱子id
                type = str(box['type'])  # 操作类型：1表示入仓，0表示出仓
                box = BoxInfo.objects.get(deviceid=box_id)

                stock = SiteBoxStock.objects.get(site_id=site_id, box_type=box.type)
                if type == '1':
                    if str(box.siteinfo_id) == str(site_id):
                        log.error(str(box_id) + '箱子已在仓库' + str(site_id))
                        continue

                    box.siteinfo_id = site_id
                else:
                    if stock.ava_num == 0:
                        log.error(str(stock.site_id) + '仓库' + str(box.type) + '型箱可用数为0.')
                        return

                    box.siteinfo = None

                history = SiteHistory(timestamp=ts, site_id=site_id, box_id=box_id, op_type=type)

                box_type_set.add(box.type)
                history.save()
                box.save()

        check_stock_ava_num(site_id, box_type_set)

    except Exception, e:
        log.error(e.message)


# 创建仓库时，初始化箱子可用数
def initialize_box_num(site_id):
    try:
        types = BoxTypeInfo.objects.all()
        with transaction.atomic():
            for t in types:
                stock = SiteBoxStock(site_id=site_id, box_type=t)
                stock.save()
    except Exception, e:
        log.error(e.message)



# 英诺尔：调度出仓接口
@csrf_exempt
@api_view(['POST'])
def dispatchout(request):
    try:
        data = json.loads(request.body)
        dispatch_id = str(data['dispatch_id'])  # 调度id
        dispatch = SiteDispatch.objects.get(did=dispatch_id)
        dispatch.status = 'dispatching'
        site = dispatch.start
        box_type_set = set()
        boxes = data['boxes']                   # 箱子数组
        ts = str(time.time())[0:10]
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])     # 箱子id
                type = '0'                      # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site=site, box_id=box_id, op_type=type)

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                box_type_set.add(box.type)
                stock = SiteBoxStock.objects.get(site=site, box_type=box.type)

                if box.siteinfo_id != site.id:
                    msg = 'Box: ' + str(box.deviceid) + ' is in site: ' + str(box.siteinfo_id)
                    response_msg = {'result': 'False', 'code': '999999', 'msg': msg, 'status': 'error'}
                    return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                box.siteinfo = None

                left_num = stock.ava_num - stock.reserve_num
                if left_num <= 0:
                    response_msg = {'result': 'False', 'code': '999999', 'msg': 'No Boxes.', 'status': 'error'}
                    return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                history.save()
                box.save()
        dispatch.save()

        check_stock_ava_num(site.id, box_type_set)
    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message, 'status': 'error'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success', 'status': 'dispatch'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 英诺尔：检查调度出仓合法性
@csrf_exempt
@api_view(['POST'])
def check_dispatch_out(request):
    try:
        data = json.loads(request.body)
        dispatch_id = str(data['dispatch_id'])  # 调度id
        dispatch = SiteDispatch.objects.get(did=dispatch_id)
        site = dispatch.start
        boxes = data['boxes']                   # 箱子数组
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])     # 箱子id
                box = BoxInfo.objects.get(deviceid=box_id)
                stock = SiteBoxStock.objects.get(site=site, box_type=box.type)

                if box.siteinfo_id != site.id:
                    msg = 'Box: ' + str(box.deviceid) + ' is in site: ' + str(box.siteinfo_id)
                    response_msg = {'result': 'False', 'code': '999999', 'msg': msg, 'status': 'error'}
                    return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                left_num = stock.ava_num - stock.reserve_num
                if left_num <= 0:
                    response_msg = {'result': 'False', 'code': '999999', 'msg': 'No Boxes.', 'status': 'error'}
                    return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message, 'status': 'error'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success', 'status': 'dispatch'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 英诺尔：调度入仓接口
@csrf_exempt
@api_view(['POST'])
def dispatchin(request):
    try:
        data = json.loads(request.body)
        dispatch_id = str(data['dispatch_id'])  # 调度id
        dispatch = SiteDispatch.objects.get(did=dispatch_id)
        site = dispatch.finish
        current_site_id = str(data['site_id'])
        if current_site_id != str(site.id):
            msg = 'Wrong site. Finish site is: ' + str(site.id)
            response_msg = {'result': 'False', 'code': '999999', 'msg': msg}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        boxes = data['boxes']
        discount = len(boxes)
        newdone = discount + dispatch.done
        if newdone > dispatch.count:
            msg = 'No more Dispatch.'
            response_msg = {'result': 'False', 'code': '999999', 'msg': msg}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif newdone == dispatch.count:
            dispatch.done = newdone
            dispatch.status = 'dispatched'
        else:
            dispatch.done = newdone

        box_type_set = set()
        ts = str(time.time())[0:10]
        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])     # 箱子id
                type = '1'                      # 操作类型：1表示入仓，0表示出仓
                history = SiteHistory(timestamp=ts, site=site, box_id=box_id, op_type=type)

                # 更新仓库箱子可用数量
                box = BoxInfo.objects.get(deviceid=box_id)
                if box.siteinfo_id == site.id:
                    msg = 'Box already in site.'
                    response_msg = {'result': 'False', 'code': '999999', 'msg': msg}
                    return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                box.ava_flag = 'Y'
                box.siteinfo = site

                box_type_set.add(box.type)

                history.save()
                box.save()

        dispatch.save()

        check_stock_ava_num(site.id, box_type_set)

    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 英诺尔：检查调度入仓合法性
@csrf_exempt
@api_view(['POST'])
def check_dispatch_in(request):
    try:
        data = json.loads(request.body)
        dispatch_id = str(data['dispatch_id'])  # 调度id
        dispatch = SiteDispatch.objects.get(did=dispatch_id)
        site = dispatch.finish
        current_site_id = str(data['site_id'])
        if current_site_id != str(site.id):
            msg = 'Wrong site. Finish site is: ' + str(site.id)
            response_msg = {'result': 'False', 'code': '999999', 'msg': msg}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        boxes = data['boxes']
        discount = len(boxes)
        newdone = discount + dispatch.done
        if newdone > dispatch.count:
            msg = 'No more Dispatch.'
            response_msg = {'result': 'False', 'code': '999999', 'msg': msg}
            return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with transaction.atomic():
            for box in boxes:
                box_id = str(box['box_id'])
                box = BoxInfo.objects.get(deviceid=box_id)
                if box.siteinfo_id == site.id:
                    msg = 'Box is already in site.'
                    response_msg = {'result': 'False', 'code': '999999', 'msg': msg}
                    return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def init_site(request):
    try:
        types = BoxTypeInfo.objects.all()
        requrl = 'http://127.0.0.1:8000/container/api/v1/cloudbox/monservice/basicInfoConfig'
        for t in types:
            for i in range(1, 21):
                num_str = '%06d' % i
                rfid = 'TEST' + str(t.id) + num_str
                body_data = {   'rfid': rfid,
                                'containerType': t.id,
                                'factory': 1,
                                'factoryLocation': 1,
                                'batteryInfo': 1,
                                'hardwareInfo': 1,
                                'manufactureTime': '1509431998000'
                            }

                req = urllib2.Request(url=requrl)
                req.add_header('Content-type', 'application/json')
                req.add_header('Authorization', '139a2d1c6f0a44909670f4e749a1397d')
                req.add_data(json.dumps(body_data))
                res_data = urllib2.urlopen(req)
                res = res_data.read()
                log.info(res)

        boxes = BoxInfo.objects.filter(tid__startswith='TEST')
        stock = {}
        stock['site_id'] = '1'

        box_list = []
        for box in boxes:
            box_para = {}
            box_para['box_id'] = box.deviceid
            box_para['type'] = 1
            box_list.append(box_para)
        stock['boxes'] = box_list

        enter_leave_site(stock)

    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)


# 出入仓完成后，检查修改可用数
def check_stock_ava_num(site_id, box_type_set):
    try:
        with transaction.atomic():
            for box_type in box_type_set:
                count = BoxInfo.objects.filter(siteinfo_id=site_id, type_id=box_type).count()
                stock = SiteBoxStock.objects.get(site_id=site_id, box_type_id=box_type)
                stock.ava_num = count
                stock.save()
    except Exception, e:
        log.error(e.message)


# 测试用，检查所有仓库可用数与实际是否相符
@csrf_exempt
@api_view(['POST'])
def check_all_num(request):
    try:
        sites = SiteInfo.objects.all()
        with transaction.atomic():
            for site in sites:
                box_types = BoxTypeInfo.objects.all()
                for box_type in box_types:
                    count = BoxInfo.objects.filter(siteinfo_id=site.id, type_id=box_type.id).count()
                    stock = SiteBoxStock.objects.get(site_id=site.id, box_type_id=box_type.id)
                    stock.ava_num = count
                    stock.save()
    except Exception, e:
        log.error(e.message)
        response_msg = {'result': 'False', 'code': '999999', 'msg': e.message}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response_msg = {'result': 'True', 'code': '000000', 'msg': 'Success'}
        return JsonResponse(response_msg, safe=True, status=status.HTTP_200_OK)








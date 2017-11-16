#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudbox.settings')

app = Celery('cloudbox')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/15', hour='*'), billing.s())
    sender.add_periodic_task(crontab(minute='*/15', hour='*'), cancel_appointment.s())
    sender.add_periodic_task(crontab(minute=1, hour=0), generate_site_stat.s())


@app.task
def billing():
    from rentservice.models import RentLeaseInfo
    from rentservice.utils import logger
    import datetime
    import pytz
    tz = pytz.timezone(settings.TIME_ZONE)
    log = logger.get_logger(__name__)
    log.info("billing begin ...")
    rent_info_list = RentLeaseInfo.objects.filter(rent_status=0)
    for rent_info in rent_info_list:
        if rent_info.rent_fee_rate == 0:
            price_per_hour = int(rent_info.box.type.price)
        else:
            price_per_hour = rent_info.rent_fee_rate
        current_time = datetime.datetime.now(tz=tz)
        rent_hour_delta = current_time.hour - rent_info.lease_start_time.hour
        rent_info.rent = price_per_hour * rent_hour_delta
        log.info("lease_info_id=%s, current rent=%s" % (rent_info.lease_info_id, rent_info.rent))
        rent_info.save()
    log.info("billing end ...")


@app.task
def cancel_appointment():
    from rentservice.models import UserAppointment
    from rentservice.models import AppointmentDetail
    from monservice.models import SiteBoxStock
    from rentservice.utils import logger
    import datetime
    import pytz
    tz = pytz.timezone(settings.TIME_ZONE)
    log = logger.get_logger(__name__)
    log.info("cancel appointment start...")
    current_time = datetime.datetime.now(tz=tz)
    start_time = current_time + datetime.timedelta(minutes=-20)
    appointment_list = UserAppointment.objects.filter(flag=0, cancel_time__gte=start_time,
                                                      cancel_time__lte=current_time)
    for appointment in appointment_list:
        detail_list = AppointmentDetail.objects.filter(appointment_id=appointment)
        for detail in detail_list:
            stock = SiteBoxStock.objects.get(site=detail.site_id, box_type=detail.box_type)
            stock.reserve_num -= detail.box_num
            stock.save()
        appointment.flag = 2
        appointment.save()
    log.info("cancel appointment end....")


@app.task
def generate_site_stat():
    from monservice.models import SiteInfo
    from rentservice.models import RentLeaseInfo
    from rentservice.models import SiteStat
    from rentservice.models import SiteStatDetail
    from monservice.models import BoxTypeInfo
    from rentservice.utils import logger
    import uuid
    import datetime
    import pytz
    tz = pytz.timezone(settings.TIME_ZONE)
    log = logger.get_logger(__name__)
    log.info("statistic site box start...")
    # 轮询所有的仓库信息
    site_list = SiteInfo.objects.all()
    box_types = BoxTypeInfo.objects.all()
    now = datetime.datetime.now(tz=tz)
    start_time = now + datetime.timedelta(days=-1)
    stat_day = start_time.strftime('%Y-%m-%d')
    for site in site_list:
        # 获取所有转出的箱子信息 上一日的所有数据
        box_out = RentLeaseInfo.objects.filter(off_site=site, lease_start_time__gte=start_time)
        # 获取所有入场的箱子信息 上一日的所有数据
        box_in = RentLeaseInfo.objects.filter(on_site=site, lease_end_time__gte=start_time)
        # 统计总数
        stat_id = str(uuid.uuid1())
        site_stat = SiteStat(stat_id=stat_id, stat_day=stat_day, total_in=box_in.count(), total_out=box_out.count(),
                             site=site)
        site_stat.save()
        # 获取不同类型箱子的in & out
        box_type_stat = []
        for box_type in box_types:
            # box out count
            out_count = box_out.filter(box__type=box_type).count()
            # box in count
            in_count = box_in.filter(box__type=box_type).count()
            stat_detail = SiteStatDetail(detail_id=str(uuid.uuid1()), box_type=box_type, box_out=out_count,
                                         box_in=in_count, sitestat=site_stat)
            box_type_stat.append(stat_detail)
        SiteStatDetail.objects.bulk_create(box_type_stat)
    log.info('statistic site box end....')


@app.task()
def send_push_message(alias_list, push_message):
    from rentservice.utils.jpush import push
    from rentservice.utils import logger
    log = logger.get_logger(__name__)
    try:
        push.push_alias(alias_list=alias_list, push_msg=push_message)
    except Exception as e:
        log.error(e)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

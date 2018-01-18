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
    # sender.add_periodic_task(crontab(minute='*/15', hour='*'), billing.s())
    sender.add_periodic_task(crontab(minute='*/15', hour='*'), cancel_appointment.s())
    sender.add_periodic_task(crontab(minute=1, hour=0), generate_site_stat.s())
    # sender.add_periodic_task(crontab(minute=15, hour=0), box_rent_fee_daily_billing.s())
    sender.add_periodic_task(crontab(minute=0, hour=1), box_rent_fee_month_billing.s())
    sender.add_periodic_task(crontab(minute='*/5', hour='*'), update_redis_auth_info.s())


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
        detail_list = AppointmentDetail.objects.filter(appointment_id=appointment, flag=0)
        for detail in detail_list:
            stock = SiteBoxStock.objects.get(site=detail.site_id, box_type=detail.box_type)
            stock.reserve_num -= detail.box_num
            stock.save()
            detail.flag = 1
            detail.save()
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


# @app.task
# def box_rent_fee_daily_billing():
#     from rentservice.models import RentLeaseInfo, EnterpriseUser, BoxRentFeeDetail
#     from rentservice.serializers import BoxRentFeeDetailSerializer, RentLeaseBoxSerializer
#     from rentservice.utils import logger
#     import datetime
#     import pytz
#     import uuid
#     tz = pytz.timezone(settings.TIME_ZONE)
#     log = logger.get_logger(__name__)
#     log.info("BoxRentFee billing begin ...")
#     current_time = datetime.datetime.now(tz=tz)
#     if RentLeaseInfo.objects.all().count() > 0:
#         user_list = RentLeaseInfo.objects.values_list('user_id', flat=True)
#         user_obj_list = EnterpriseUser.objects.filter(user_id__in=user_list)
#         # log.info("box_rent_fee_billing: user_list=%s" % user_list)
#         for user in user_obj_list:
#             off_site_counts = RentLeaseInfo.objects.filter(user_id=user, last_update_time__day=current_time.day - 1,
#                                                            lease_start_time__day=current_time.day - 1).count()
#             on_site_counts = RentLeaseInfo.objects.filter(user_id=user, last_update_time__day=current_time.day - 1,
#                                                           lease_end_time__day=current_time.day - 1).count()
#             log.info("box_rent_fee_billing: off_site_counts=%s, on_site_counts=%s" % (off_site_counts, on_site_counts))
#             try:
#                 log.info("box_rent_fee_billing: begin compute")
#                 user_lease_info_list = RentLeaseInfo.objects.filter(user_id=user)
#                 if user_lease_info_list.count() == 0:
#                     log.info("box_rent_fee_billing: user_lease_info_list is null")
#                 log.info("box_rent_fee_billing: user_lease_info_list = %s" %
#                          RentLeaseBoxSerializer(user_lease_info_list, many=True).data)
#                 user_total_rent_fee = 0
#                 for lease in user_lease_info_list:
#                     if lease.rent_fee_rate == 0:
#                         price_per_hour = int(lease.box.type.price)
#                     else:
#                         price_per_hour = lease.rent_fee_rate
#                     log.info("box_rent_fee_billing: id=%s, price_per_hour=%s, rent_fee_rate=%s" %
#                              (lease.lease_info_id, price_per_hour, lease.rent_fee_rate))
#                     if lease.rent_status == 0:
#                         user_total_rent_fee = user_total_rent_fee + price_per_hour * 24
#                         log.info("box_rent_fee_billing: still billing user_total_rent_fee=%s" % user_total_rent_fee)
#                     else:
#                         delta_hour = current_time.hour - lease.lease_end_time.hour
#                         delta_day = current_time.day - lease.lease_end_time.day
#                         delta_month = current_time.month - lease.lease_end_time.month
#                         delta_year = current_time.month - lease.lease_end_time.year
#                         if (delta_hour <= 24 and delta_hour > 0) and delta_day == 0 \
#                                 and delta_month == 0 and delta_year == 0:
#                             user_total_rent_fee = user_total_rent_fee + price_per_hour * (delta_hour)
#                             log.info("lease id = %s, box lease finished, the last delat hour is %s, rent rate is %s"
#                                      % (lease.lease_info_id, delta_hour, price_per_hour))
#                         else:
#                             log.info("lease id = %s, box lease finished, terminate rent_billing" % lease.lease_info_id)
#                     lease.last_update_time = current_time
#                     lease.save()
#                     log.info("box_rent_fee_billing: update last_update_time succ")
#                 box_rent_fee = BoxRentFeeDetail(detail_id=uuid.uuid1(), enterprise=user.enterprise,
#                                                 user=user, date=current_time, off_site_nums=off_site_counts,
#                                                 on_site_nums=on_site_counts, rent_fee=user_total_rent_fee)
#                 box_rent_fee.save()
#                 log.info("save box_rent_fee == %s" % BoxRentFeeDetailSerializer(box_rent_fee).data)
#                 log.info("box_rent_fee_billing: compute finsih")
#             except Exception, e:
#                 log.error(repr(e))
#     else:
#         log.info("no rent lease info. do nothing")
#     log.info("BoxRentFee billing end ...")


@app.task
def box_rent_fee_month_billing():
    from rentservice.models import BoxRentFeeDetail, BoxRentFeeByMonth, EnterpriseInfo
    from rentservice.utils import logger
    import datetime
    import pytz
    import uuid
    tz = pytz.timezone(settings.TIME_ZONE)
    log = logger.get_logger(__name__)
    log.info("BoxRentFeeByMonth billing begin ...")
    current_time = datetime.datetime.now(tz=tz)
    if BoxRentFeeDetail.objects.all().count() > 0:
        log.info("box_rent_fee_month_billing: compute begin")
        try:
            enterprise_list = BoxRentFeeDetail.objects.values('enterprise').distinct()
            for enterprise in enterprise_list:
                enterprise_obj = EnterpriseInfo.objects.get(enterprise_id=enterprise['enterprise'])
                query_list = BoxRentFeeDetail.objects.filter(enterprise=enterprise_obj,
                                                             date__year=current_time.year,
                                                             date__month=current_time.month)
                off_site_box_nums_month = 0
                on_site_box_nums_month = 0
                rent_fee_month = 0
                for box_rent_day in query_list:
                    rent_fee_month = rent_fee_month + box_rent_day.rent_fee
                    on_site_box_nums_month = on_site_box_nums_month + box_rent_day.on_site_nums
                    off_site_box_nums_month = off_site_box_nums_month + box_rent_day.off_site_nums
                log.info("enterprise_id = %s, rent_fee_month=%s, on_site_box_nums_month=%s,off_site_box_nums_month=%s"
                         % (enterprise['enterprise'], rent_fee_month, on_site_box_nums_month, off_site_box_nums_month))
                try:
                    box_rent_bill_month = BoxRentFeeByMonth.objects.get(enterprise=enterprise_obj,
                                                                        date__year=current_time.year,
                                                                        date__month=current_time.month)
                    box_rent_bill_month.rent_fee = rent_fee_month
                    box_rent_bill_month.off_site_nums = off_site_box_nums_month
                    box_rent_bill_month.on_site_nums = on_site_box_nums_month
                    box_rent_bill_month.save()
                except BoxRentFeeByMonth.DoesNotExist, e:
                    month_date = datetime.datetime(year=current_time.year, month=current_time.month, day=1, hour=12,
                                                   tzinfo=tz)
                    box_rent_fee = BoxRentFeeByMonth(detail_id=uuid.uuid1(), enterprise=enterprise_obj,
                                                     date=month_date, off_site_nums=off_site_box_nums_month,
                                                     on_site_nums=on_site_box_nums_month,
                                                     rent_fee=rent_fee_month)
                    box_rent_fee.save()
                    log.error(repr(e))
        except Exception, e:
            log.error(repr(e))
        log.info("box_rent_fee_month_billing: compute finsih")
    else:
        log.info("no BoxRentFeeDetail records. do nothing")
    log.info("BoxRentFeeByMonth billing end ...")


@app.task
def update_redis_auth_info():
    from rentservice.models import AccessGroup, AccessUrlGroup, AuthUserGroup
    from rentservice.serializers import AccessGroupSerializer, AuthUserGroupSerializer, AccessUrlGroupSerializer
    from rentservice.utils import logger
    from rentservice.utils.redistools import RedisTool
    PERMISSION_GROUP_HASH = 'permissions_group_hash'
    PERMISSION_URL_HASH = 'permissions_url_hash'
    log = logger.get_logger(__name__)
    log.info("update_redis_auth_info begin")
    try:
        redis_pool = RedisTool()
        conn = redis_pool.get_connection()
        access_group_ret = AccessGroup.objects.all()
        access_group_list = AccessGroupSerializer(access_group_ret, many=True).data
        groupid_group_dic = {}
        for item in access_group_list:
            groupid_group_dic[item['access_group_id']] = item['group']
        ret = AuthUserGroup.objects.all()
        auth_user_group = AuthUserGroupSerializer(ret, many=True).data
        for item in auth_user_group:
            conn.hset(PERMISSION_GROUP_HASH, item['user_token'], groupid_group_dic[item['group']])
        for item_access_group in access_group_list:
            ret = AccessUrlGroup.objects.filter(access_group__group=item_access_group['group'])
            access_url_list = []
            access_url_group = AccessUrlGroupSerializer(ret, many=True).data
            for item in access_url_group:
                access_url_list.append(item['access_url_set'])
            if access_url_list:
                final_hash_value = ','.join(access_url_list)
            else:
                final_hash_value = ''
            if final_hash_value:
                conn.hset(PERMISSION_URL_HASH, item_access_group['group'], final_hash_value)
    except Exception, e:
        log.error(repr(e))
    log.info("update_redis_auth_info end")


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task
def update_box_bill_daily():
    from rentservice.models import BoxRentFeeDetail, RentLeaseInfo, EnterpriseUser
    from rentservice.utils import logger
    import uuid
    import datetime
    import pytz
    from django.conf import settings
    from django.db import transaction
    log = logger.get_logger(__name__)
    timezone = pytz.timezone(settings.TIME_ZONE)
    current_time = datetime.datetime.now(tz=timezone)
    log.info("update_box_bill_daily: compute begin")
    try:
        user_list = RentLeaseInfo.objects.filter(rent_status=1, sum_flag=0).values_list('user_id', flat=True)
        user_obj_list = EnterpriseUser.objects.select_related('enterprise').filter(user_id__in=user_list)
        log.info("update_box_bill_daily: user_list = %s" % user_list)
        for user in user_obj_list:
            off_site_counts = 0
            on_site_counts = RentLeaseInfo.objects.filter(user_id=user, rent_status=1, sum_flag=0).count()
            rent_lease_info_list = RentLeaseInfo.objects.select_for_update().filter(user_id=user, rent_status=1, sum_flag=0)
            user_rent_fee_sum = 0
            with transaction.atomic():
                for rent_lease_info in rent_lease_info_list:
                    user_rent_fee_sum = user_rent_fee_sum + rent_lease_info.rent
                    rent_lease_info.sum_flag = 1
                    rent_lease_info.last_update_time = current_time
                    rent_lease_info.save()
                log.info("update_box_bill_daily: off_site_counts=%s, on_site_counts=%s" % (off_site_counts, on_site_counts))
                box_rent_fee = BoxRentFeeDetail(detail_id=uuid.uuid1(), enterprise=user.enterprise,
                                                user=user, date=current_time,
                                                off_site_nums=off_site_counts,
                                                on_site_nums=on_site_counts, rent_fee=user_rent_fee_sum)
                box_rent_fee.save()
    except Exception, e:
        log.error(repr(e))
    log.info("update_box_bill_daily: compute finsih")


@app.task
def update_box_bill_month_async():
    from rentservice.models import BoxRentFeeDetail, EnterpriseInfo, BoxRentFeeByMonth
    from rentservice.utils import logger
    import uuid
    import datetime
    import pytz
    from django.conf import settings
    log = logger.get_logger(__name__)
    timezone = pytz.timezone(settings.TIME_ZONE)
    log.info("update_box_bill_daily: compute begin")
    current_time = datetime.datetime.now(tz=timezone)
    if BoxRentFeeDetail.objects.all().count() > 0:
        log.info("box_rent_fee_month_billing: compute begin")
        try:
            enterprise_list = BoxRentFeeDetail.objects.values('enterprise').distinct()
            for enterprise in enterprise_list:
                enterprise_obj = EnterpriseInfo.objects.get(enterprise_id=enterprise['enterprise'])
                query_list = BoxRentFeeDetail.objects.filter(enterprise=enterprise_obj,
                                                                 date__year=current_time.year,
                                                                 date__month=current_time.month)
                off_site_box_nums_month = 0
                on_site_box_nums_month = 0
                rent_fee_month = 0
                for box_rent_day in query_list:
                    rent_fee_month = rent_fee_month + box_rent_day.rent_fee
                    on_site_box_nums_month = on_site_box_nums_month + box_rent_day.on_site_nums
                    off_site_box_nums_month = off_site_box_nums_month + box_rent_day.off_site_nums
                log.info(
                    "enterprise_id = %s, rent_fee_month=%s, on_site_box_nums_month=%s,off_site_box_nums_month=%s"
                    % (enterprise['enterprise'], rent_fee_month, on_site_box_nums_month, off_site_box_nums_month))
                try:
                    box_rent_bill_month = BoxRentFeeByMonth.objects.get(enterprise=enterprise_obj,
                                                                        date__year=current_time.year,
                                                                        date__month=current_time.month)
                    box_rent_bill_month.rent_fee = rent_fee_month
                    box_rent_bill_month.off_site_nums = off_site_box_nums_month
                    box_rent_bill_month.on_site_nums = on_site_box_nums_month
                    box_rent_bill_month.save()
                except BoxRentFeeByMonth.DoesNotExist, e:
                    month_date = datetime.datetime(year=current_time.year, month=current_time.month, day=1, hour=12,
                                                   tzinfo=timezone)
                    box_rent_fee = BoxRentFeeByMonth(detail_id=uuid.uuid1(), enterprise=enterprise_obj,
                                                     date=month_date, off_site_nums=off_site_box_nums_month,
                                                     on_site_nums=on_site_box_nums_month,
                                                     rent_fee=rent_fee_month)
                    box_rent_fee.save()
                    log.error(repr(e))
        except Exception, e:
            log.error(repr(e))
        log.info("box_rent_fee_month_billing: compute finsih")
    else:
        log.info("no BoxRentFeeDetail records. do nothing")

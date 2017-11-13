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
        price_per_hour = int(rent_info.box.type.price)
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


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

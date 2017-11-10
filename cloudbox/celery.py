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


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

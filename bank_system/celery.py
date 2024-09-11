from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_system.settings')

app = Celery('bank_system')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send-payment-reminders-every-day':{
        'task': 'loan.tasks.send_payment_reminders',
        'schedule': crontab(hour=7, minute=0),
    },
}

app.autodiscover_tasks()
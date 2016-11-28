from __future__ import absolute_import

import os

# Necessary for Celery to find iron_celery for transport ironmq://
from celery import Celery

from django.conf import settings

# Set the default Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lily.settings')

app = Celery('lily', broker=settings.BROKER_URL)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

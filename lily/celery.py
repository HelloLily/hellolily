from __future__ import absolute_import
import os

from django.apps import apps
from celery import Celery


# Set the default Django settings module.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lily.settings.django_settings")

# Setup celery app.
app = Celery('lily')
app.config_from_object('lily.settings.celery_settings:settings')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

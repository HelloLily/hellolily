# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.db import models, migrations
from django.utils.timezone import make_aware, get_default_timezone


def set_status(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")
    created_datetime = make_aware(datetime(2015, 3, 1), get_default_timezone())

    for account in Account.objects.filter(created__gte=created_datetime, status='').exclude(customer_id=''):
        account.status = 'active'
        account.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20150420_1006'),
    ]

    operations = [
        migrations.RunPython(set_status, do_nothing),
    ]

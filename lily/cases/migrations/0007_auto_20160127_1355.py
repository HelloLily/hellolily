# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0006_case_billing_checked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='assigned_to',
            field=models.ForeignKey(related_name='assigned_cases', verbose_name='assigned to', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(related_name='created_cases', verbose_name='created by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

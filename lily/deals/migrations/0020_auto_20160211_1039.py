# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contacts', '0005_auto_20150527_0941'),
        ('deals', '0019_auto_20160204_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='contact',
            field=models.ForeignKey(verbose_name='contact', blank=True, to='contacts.Contact', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deal',
            name='created_by',
            field=models.ForeignKey(related_name='created_deals', verbose_name='created by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

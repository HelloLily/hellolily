# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0002_auto_20150423_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='is_checked',
            field=models.BooleanField(default=False, choices=[(False, 'No'), (True, 'Yes')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deal',
            name='quote_id',
            field=models.CharField(max_length=255, verbose_name='Freedom id', blank=True),
            preserve_default=True,
        ),
    ]

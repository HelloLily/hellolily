# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.utils.date_time


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0004_auto_20151002_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='expires',
            field=models.DateField(default=lily.utils.date_time.week_from_now, verbose_name='expires'),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0003_auto_20150511_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='quote_id',
            field=models.CharField(max_length=255, verbose_name='Freedom quote id', blank=True),
            preserve_default=True,
        ),
    ]

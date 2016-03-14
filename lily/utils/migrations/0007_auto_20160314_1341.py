# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0006_auto_20150714_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street_number',
            field=models.IntegerField(null=True, verbose_name='street number', blank=True),
            preserve_default=True,
        ),
    ]

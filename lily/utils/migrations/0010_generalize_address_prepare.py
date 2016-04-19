# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0009_remove_phonenumber_raw_input'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='address',
            field=models.CharField(max_length=255, verbose_name='address', blank=True),
            preserve_default=True,
        ),
    ]

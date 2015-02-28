# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20150218_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='import_id',
            field=models.CharField(max_length=100, null=True, verbose_name='import id', blank=True),
            preserve_default=True,
        ),
    ]

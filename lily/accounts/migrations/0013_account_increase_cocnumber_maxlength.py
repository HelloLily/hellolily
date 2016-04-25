# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_account_status_cleanup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='cocnumber',
            field=models.CharField(max_length=20, verbose_name='coc number', blank=True),
            preserve_default=True,
        ),
    ]

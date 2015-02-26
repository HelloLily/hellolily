# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_account_import_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='import_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='import id', db_index=True, blank=True),
            preserve_default=True,
        ),
    ]

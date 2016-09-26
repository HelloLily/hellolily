# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0016_set_first_sync_current_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaccount',
            name='deleted',
            field=models.DateTimeField(verbose_name='deleted'),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0021_auto_20161128_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailaccount',
            old_name='first_sync_finished',
            new_name='full_sync_finished',
        ),
        migrations.AddField(
            model_name='emailaccount',
            name='sync_failure_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]

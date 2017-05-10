# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0028_rename_full_sync_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaccount',
            name='only_new',
            field=models.NullBooleanField(default=False),
        ),
    ]

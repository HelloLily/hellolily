# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0014_auto_20160809_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaccount',
            name='first_sync_finished',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0024_migrate_public_setting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailaccount',
            name='public',
        ),
    ]

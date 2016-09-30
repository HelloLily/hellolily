# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0013_auto_20160922_1154'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='assigned_to_groups',
            new_name='assigned_to_teams',
        ),
    ]

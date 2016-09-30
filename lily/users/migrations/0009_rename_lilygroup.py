# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0014_rename_case_assigned_to_groups'),
        ('users', '0008_auto_20160406_1122'),
    ]

    operations = [
        migrations.RenameModel(
            'LilyGroup', 'Team'
        ),
        migrations.RenameField(
            model_name='lilyuser',
            old_name='lily_groups',
            new_name='teams',
        )
    ]

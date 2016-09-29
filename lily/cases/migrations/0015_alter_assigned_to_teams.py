# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0014_rename_case_assigned_to_groups'),
        ('users', '0009_rename_lilygroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='assigned_to_teams',
            field=models.ManyToManyField(related_name='assigned_to_teams', null=True, to='users.Team', blank=True),
            preserve_default=True,
        ),
    ]

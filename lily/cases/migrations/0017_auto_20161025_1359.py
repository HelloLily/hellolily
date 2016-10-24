# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0016_case_newly_assigned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='assigned_to_teams',
            field=models.ManyToManyField(related_name='assigned_to_teams', to='users.Team', blank=True),
        ),
    ]

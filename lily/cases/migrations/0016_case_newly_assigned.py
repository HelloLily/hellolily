# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0015_alter_assigned_to_teams'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='newly_assigned',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

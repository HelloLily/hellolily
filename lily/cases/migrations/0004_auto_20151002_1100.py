# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0003_case_assigned_to_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='priority',
            field=models.SmallIntegerField(default=0, verbose_name='priority', choices=[(0, 'Low'), (1, 'Medium'), (2, 'High'), (3, 'Critical')]),
            preserve_default=True,
        ),
    ]

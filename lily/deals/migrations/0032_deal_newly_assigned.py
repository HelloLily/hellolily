# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0031_auto_20160922_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='newly_assigned',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

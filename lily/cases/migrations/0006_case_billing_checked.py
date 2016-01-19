# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0005_auto_20151012_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='billing_checked',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

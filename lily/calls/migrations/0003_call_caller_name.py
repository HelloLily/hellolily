# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0002_auto_20161125_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='caller_name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]

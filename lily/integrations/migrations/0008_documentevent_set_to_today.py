# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0007_slackdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentevent',
            name='set_to_today',
            field=models.BooleanField(default=False),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0018_auto_20160922_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailmessage',
            name='is_removed',
        ),
    ]

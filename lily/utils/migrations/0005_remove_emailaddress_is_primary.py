# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0004_auto_20150520_0940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailaddress',
            name='is_primary',
        ),
    ]

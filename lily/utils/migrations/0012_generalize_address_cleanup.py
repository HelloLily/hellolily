# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0011_generalize_address_data_migrate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='street',
        ),
        migrations.RemoveField(
            model_name='address',
            name='street_number',
        ),
        migrations.RemoveField(
            model_name='address',
            name='complement',
        ),
    ]

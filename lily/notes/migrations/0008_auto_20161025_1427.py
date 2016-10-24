# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_auto_20160922_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Note'), (1, 'Call'), (2, 'Meetup')]),
        ),
    ]

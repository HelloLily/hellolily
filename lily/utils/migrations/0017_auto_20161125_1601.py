# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0016_remove_historylistitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='status', choices=[(2, 'Primary'), (1, 'Other'), (0, 'Inactive')]),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='status', choices=[(0, 'Inactive'), (1, 'Active')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20161125_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilyuser',
            name='internal_number',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='internal number', blank=True),
        ),
    ]

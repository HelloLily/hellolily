# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20161003_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='lilyuser',
            name='internal_number',
            field=models.IntegerField(max_length=3, null=True, verbose_name='internal number', blank=True),
            preserve_default=True,
        ),
    ]

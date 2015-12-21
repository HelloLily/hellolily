# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0012_auto_20151203_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='imported_from',
            field=models.CharField(max_length=50, null=True, verbose_name='imported from', blank=True),
            preserve_default=True,
        ),
    ]

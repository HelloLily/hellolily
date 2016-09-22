# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0009_auto_20160610_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='deleted',
            field=models.DateTimeField(verbose_name='deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='deleted',
            field=models.DateTimeField(verbose_name='deleted'),
            preserve_default=True,
        ),
    ]

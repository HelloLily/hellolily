# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0005_auto_20160610_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='deleted',
            field=models.DateTimeField(verbose_name='deleted'),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0020_auto_20160211_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='amount_once',
            field=models.DecimalField(default=0, verbose_name='one-time cost', max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_recurring',
            field=models.DecimalField(default=0, verbose_name='recurring costs', max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
    ]

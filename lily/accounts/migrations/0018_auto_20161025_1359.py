# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20160922_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountstatus',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]

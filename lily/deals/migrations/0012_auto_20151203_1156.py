# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0011_auto_20151201_1455'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dealnextstep',
            options={'ordering': ['position']},
        ),
        migrations.AddField(
            model_name='dealnextstep',
            name='position',
            field=models.IntegerField(default=9, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]),
            preserve_default=True,
        ),
    ]

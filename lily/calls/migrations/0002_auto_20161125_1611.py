# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Ringing'), (1, 'Answered'), (2, 'Hung up')]),
        ),
        migrations.AlterField(
            model_name='call',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Inbound'), (1, 'Outbound')]),
        ),
    ]

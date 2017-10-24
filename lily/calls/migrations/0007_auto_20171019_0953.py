# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0006_auto_20171011_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callparticipant',
            name='internal_number',
            field=models.CharField(default='', max_length=5, verbose_name='Interal number', blank=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='callparticipant',
            unique_together=set([('tenant', 'name', 'number', 'internal_number')]),
        ),
    ]

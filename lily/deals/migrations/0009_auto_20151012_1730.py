# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0008_auto_20150930_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='contacted_by',
            field=models.IntegerField(blank=True, max_length=255, null=True, verbose_name='contacted us by', choices=[(0, 'Quote'), (1, 'Contact form'), (2, 'Phone'), (3, 'Web chat'), (4, 'E-mail'), (6, 'Instant connect'), (5, 'Other')]),
            preserve_default=True,
        ),
    ]

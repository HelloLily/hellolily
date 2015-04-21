# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20150227_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='status',
            field=models.CharField(blank=True, max_length=50, verbose_name='status', choices=[(b'inactive', 'Inactive'), (b'active', 'Active'), (b'pending', 'Pending'), (b'prev_customer', 'Previous customer'), (b'bankrupt', 'Bankrupt'), (b'unknown', 'Unknown')]),
            preserve_default=True,
        ),
    ]

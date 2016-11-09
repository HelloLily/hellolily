# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0003_tenant_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='currency',
            field=models.CharField(blank=True, max_length=3, verbose_name=b'currency', choices=[(b'EUR', 'Euro'), (b'GBP', 'British pound'), (b'USD', 'United States dollar'), (b'ZAR', 'South African rand'), (b'NOR', 'Norwegian krone'), (b'DKK', 'Danish krone'), (b'SEK', 'Swedish krone'), (b'CHF', 'Swiss franc')]),
            preserve_default=True,
        ),
    ]

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
            name='currency',
            field=models.CharField(max_length=3, verbose_name='currency', choices=[(b'EUR', 'Euro'), (b'GBP', 'British pound'), (b'USD', 'United States dollar'), (b'ZAR', 'South African rand'), (b'NOR', 'Norwegian krone'), (b'DKK', 'Danish krone'), (b'SEK', 'Swedish krone'), (b'CHF', 'Swiss franc')]),
            preserve_default=True,
        ),
    ]

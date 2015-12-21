# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0013_deal_imported_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='found_through',
            field=models.IntegerField(blank=True, max_length=255, null=True, verbose_name='found us through', choices=[(0, 'Search engine'), (1, 'Social media'), (2, 'Talk with employee'), (3, 'Existing customer'), (5, 'Radio'), (4, 'Other')]),
            preserve_default=True,
        ),
    ]

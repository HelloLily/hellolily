# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0006_auto_20150901_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='contacted_by',
            field=models.IntegerField(blank=True, max_length=255, null=True, verbose_name='contacted us by', choices=[(0, 'Quote'), (1, 'Contact form'), (2, 'Phone'), (3, 'Web chat'), (4, 'E-mail'), (5, 'Other')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deal',
            name='found_through',
            field=models.IntegerField(blank=True, max_length=255, null=True, verbose_name='found us through', choices=[(0, 'Search engine'), (1, 'Social media'), (2, 'Talk with employee'), (3, 'Existing customer'), (4, 'Other')]),
            preserve_default=True,
        ),
    ]

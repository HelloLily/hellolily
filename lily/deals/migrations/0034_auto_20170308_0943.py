# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0033_auto_20161025_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='contacted_by',
            field=models.ForeignKey(related_name='deals', blank=True, to='deals.DealContactedBy', null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='found_through',
            field=models.ForeignKey(related_name='deals', blank=True, to='deals.DealFoundThrough', null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='why_customer',
            field=models.ForeignKey(related_name='deals', blank=True, to='deals.DealWhyCustomer', null=True),
        ),
    ]

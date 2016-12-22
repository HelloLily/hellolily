# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0032_deal_newly_assigned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealcontactedby',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dealfoundthrough',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dealnextstep',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dealstatus',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dealwhycustomer',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dealwhylost',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]

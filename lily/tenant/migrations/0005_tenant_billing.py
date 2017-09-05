# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
        ('tenant', '0004_tenant_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='billing',
            field=models.ForeignKey(blank=True, to='billing.Billing', null=True),
        ),
    ]

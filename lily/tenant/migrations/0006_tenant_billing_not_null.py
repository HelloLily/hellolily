# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0005_tenant_billing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenant',
            name='billing',
            field=models.ForeignKey(to='billing.Billing'),
        ),
    ]

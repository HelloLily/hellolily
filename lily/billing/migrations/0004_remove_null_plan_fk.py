# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_create_billing_objects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='plan',
            field=models.ForeignKey(to='billing.Plan'),
        ),
    ]

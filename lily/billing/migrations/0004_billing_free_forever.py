# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_create_billing_objects'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='free_forever',
            field=models.BooleanField(default=False),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0003_call_caller_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]

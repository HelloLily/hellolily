# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0014_webhook'),
        ('users', '0013_lilyuser_internal_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='lilyuser',
            name='webhooks',
            field=models.ManyToManyField(to='utils.Webhook', null=True, blank=True),
            preserve_default=True,
        ),
    ]

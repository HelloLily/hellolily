# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_lilyuser_webhooks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilyuser',
            name='webhooks',
            field=models.ManyToManyField(to='utils.Webhook', blank=True),
            preserve_default=True,
        ),
    ]

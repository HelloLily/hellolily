# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_lilyuser_lily_groups'),
        ('cases', '0002_auto_20150218_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='assigned_to_groups',
            field=models.ManyToManyField(related_name='assigned_to_groups', null=True, verbose_name='assigned to teams', to='users.LilyGroup', blank=True),
            preserve_default=True,
        ),
    ]

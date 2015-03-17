# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_lilygroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='lilyuser',
            name='lily_groups',
            field=models.ManyToManyField(related_query_name=b'user', related_name='user_set', verbose_name='Lily groups', to='users.LilyGroup', blank=True),
            preserve_default=True,
        ),
    ]

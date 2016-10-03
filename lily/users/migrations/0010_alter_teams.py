# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_rename_lilygroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilyuser',
            name='teams',
            field=models.ManyToManyField(related_query_name=b'user', related_name='user_set', verbose_name='Teams', to='users.Team', blank=True),
            preserve_default=True,
        ),
    ]

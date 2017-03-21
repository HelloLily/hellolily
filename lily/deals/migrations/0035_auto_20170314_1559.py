# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20161207_1319'),
        ('deals', '0034_auto_20170308_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='assigned_to_teams',
            field=models.ManyToManyField(to='users.Team', blank=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='assigned_to',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]

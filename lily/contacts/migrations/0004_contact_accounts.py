# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20150227_1424'),
        ('contacts', '0003_auto_20150227_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='accounts',
            field=models.ManyToManyField(to='accounts.Account', through='contacts.Function'),
            preserve_default=True,
        ),
    ]

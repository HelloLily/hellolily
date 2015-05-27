# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_contact_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='accounts',
            field=models.ManyToManyField(related_name='contacts', through='contacts.Function', to='accounts.Account'),
            preserve_default=True,
        ),
    ]

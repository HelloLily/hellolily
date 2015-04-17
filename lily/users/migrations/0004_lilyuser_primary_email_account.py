# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0002_emailmessage_is_removed'),
        ('users', '0003_lilyuser_lily_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='lilyuser',
            name='primary_email_account',
            field=models.ForeignKey(blank=True, to='email.EmailAccount', null=True),
            preserve_default=True,
        ),
    ]

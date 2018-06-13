# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_account_increase_cocnumber_maxlength'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='email_addresses',
            field=models.ManyToManyField(
                to='utils.EmailAddress',
                verbose_name='list of email addresses',
                blank=True
            ),
            preserve_default=True,
        ),
    ]

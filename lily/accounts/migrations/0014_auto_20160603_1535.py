# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.utils.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_account_increase_cocnumber_maxlength'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='email_addresses',
            field=lily.utils.models.fields.EmailAddressFormSetField(to='utils.EmailAddress',
                                                                    verbose_name='list of email addresses',
                                                                    blank=True),
            preserve_default=True,
        ),
    ]

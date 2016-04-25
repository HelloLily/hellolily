# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_account_status_data_migrate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='status',
        ),
        migrations.AlterField(
            model_name='account',
            name='status_id',
            # Set db_column, so Django doens't add _id when changing the column to a foreign key.
            field=models.ForeignKey(related_name='accounts', verbose_name='status', to='accounts.AccountStatus',
                                    db_column='status_id'),
            preserve_default=True,
        )
    ]

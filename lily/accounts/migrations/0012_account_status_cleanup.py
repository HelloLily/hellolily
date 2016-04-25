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
            name='status_old',
        ),
        migrations.AlterField(
            model_name='account',
            name='status',
            field=models.ForeignKey(related_name='accounts', verbose_name='status', to='accounts.AccountStatus'),
            preserve_default=True,
        )
    ]

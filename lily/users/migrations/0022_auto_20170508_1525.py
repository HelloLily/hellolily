# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_lilyuser_add_to_account_admin_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lilyuser',
            name='info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='users.UserInfo', null=True),
        ),
        migrations.AlterField(
            model_name='lilyuser',
            name='primary_email_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='email.EmailAccount', null=True),
        ),
    ]

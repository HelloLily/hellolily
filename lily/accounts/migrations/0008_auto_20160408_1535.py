# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.accounts.models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20160224_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='deleted',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='logo',
            field=models.ImageField(upload_to=lily.accounts.models.get_account_logo_upload_path, verbose_name='logo', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
            preserve_default=True,
        ),
    ]

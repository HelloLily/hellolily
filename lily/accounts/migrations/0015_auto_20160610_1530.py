# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.accounts.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20160603_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='assigned_to',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='bankaccountnumber',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='bic',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='cocnumber',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='customer_id',
            field=models.CharField(max_length=32, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='iban',
            field=models.CharField(max_length=40, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='import_id',
            field=models.CharField(default=b'', max_length=100, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='legalentity',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='logo',
            field=models.ImageField(upload_to=lily.accounts.models.get_account_logo_upload_path, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='status',
            field=models.ForeignKey(related_name='accounts', to='accounts.AccountStatus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='taxnumber',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
    ]

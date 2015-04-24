# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='import_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='import id', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='account',
            field=models.ForeignKey(verbose_name='account', to='accounts.Account', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_once',
            field=models.DecimalField(default=0, verbose_name='one-time cost', max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_recurring',
            field=models.DecimalField(default=0, verbose_name='recurring costs', max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='assigned_to',
            field=models.ForeignKey(verbose_name='assigned to', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='expected_closing_date',
            field=models.DateField(null=True, verbose_name='expected closing date'),
            preserve_default=True,
        ),
    ]

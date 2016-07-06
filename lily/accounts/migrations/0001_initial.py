# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields
import lily.utils.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('customer_id', models.CharField(max_length=32, verbose_name='customer id', blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='company name')),
                ('flatname', models.CharField(max_length=255, blank=True)),
                ('status', models.CharField(blank=True, max_length=50, verbose_name='status', choices=[(b'bankrupt', 'bankrupt'), (b'prev_customer', 'previous customer')])),
                ('company_size', models.CharField(blank=True, max_length=15, verbose_name='company size', choices=[(b'1', '1'), (b'2', '2-10'), (b'11', '11-50'), (b'51', '51-200'), (b'201', '201-1000'), (b'1001', '1001-5000'), (b'5001', '5001-10000'), (b'10001', '10001+')])),
                ('logo', models.ImageField(upload_to=b'images/profile/account', verbose_name='logo', blank=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('legalentity', models.CharField(max_length=20, verbose_name='legal entity', blank=True)),
                ('taxnumber', models.CharField(max_length=20, verbose_name='tax number', blank=True)),
                ('bankaccountnumber', models.CharField(max_length=20, verbose_name='bank account number', blank=True)),
                ('cocnumber', models.CharField(max_length=10, verbose_name='coc number', blank=True)),
                ('iban', models.CharField(max_length=40, verbose_name='iban', blank=True)),
                ('bic', models.CharField(max_length=20, verbose_name='bic', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'account',
                'verbose_name_plural': 'accounts',
            },
            bases=(models.Model, ),
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('website', models.URLField(max_length=255, verbose_name='website')),
                ('is_primary', models.BooleanField(default=False, verbose_name='primary website')),
                ('account', models.ForeignKey(related_name='websites', to='accounts.Account')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'website',
                'verbose_name_plural': 'websites',
            },
            bases=(models.Model,),
        ),
    ]

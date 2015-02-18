# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('priority', models.SmallIntegerField(verbose_name='priority', choices=[(0, 'Low'), (1, 'Medium'), (2, 'High'), (3, 'Critical')])),
                ('subject', models.CharField(max_length=255, verbose_name='subject')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('expires', models.DateField(default=datetime.datetime.today, verbose_name='expires')),
                ('account', models.ForeignKey(verbose_name='account', blank=True, to='accounts.Account', null=True)),
                ('assigned_to', models.ForeignKey(related_name='assigned_to', verbose_name='assigned to', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'case',
                'verbose_name_plural': 'cases',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CaseStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('status', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name_plural': 'case statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CaseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=255, db_index=True)),
                ('use_as_filter', models.BooleanField(default=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='casestatus',
            unique_together=set([('tenant', 'position')]),
        ),
    ]

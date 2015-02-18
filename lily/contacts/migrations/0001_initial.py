# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.utils.models.mixins
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=255, verbose_name='first name', blank=True)),
                ('preposition', models.CharField(max_length=100, verbose_name='preposition', blank=True)),
                ('last_name', models.CharField(max_length=255, verbose_name='last name', blank=True)),
                ('gender', models.IntegerField(default=2, verbose_name='gender', choices=[(0, 'Male'), (1, 'Female'), (2, 'Unknown/Other')])),
                ('title', models.CharField(max_length=20, verbose_name='title', blank=True)),
                ('status', models.IntegerField(default=1, verbose_name='status', choices=[(0, 'Inactive'), (1, 'Active')])),
                ('picture', models.ImageField(upload_to=b'images/profile/contact', verbose_name='picture', blank=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('salutation', models.IntegerField(default=1, verbose_name='salutation', choices=[(0, 'Formal'), (1, 'Informal')])),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
            bases=(models.Model, lily.utils.models.mixins.CaseClientModelMixin),
        ),
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=50, verbose_name='title', blank=True)),
                ('department', models.CharField(max_length=50, verbose_name='department', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('account', models.ForeignKey(related_name='functions', to='accounts.Account')),
                ('contact', models.ForeignKey(related_name='functions', to='contacts.Contact')),
            ],
            options={
                'verbose_name': 'function',
                'verbose_name_plural': 'functions',
            },
            bases=(models.Model,),
        ),
    ]

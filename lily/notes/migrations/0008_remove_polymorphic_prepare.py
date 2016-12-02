# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_extensions.db.fields

# Trigger migrations for Travis testing.


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0004_tenant_currency'),
        ('contenttypes', '0001_initial'),
        ('notes', '0007_auto_20160922_1154'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=False, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=False, verbose_name='modified')),
                ('deleted', models.DateTimeField(null=True, verbose_name='deleted', blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('content', models.TextField()),
                ('type', models.SmallIntegerField(default=0, max_length=2, choices=[(0, 'Note'), (1, 'Call'), (2, 'Meetup')])),
                ('object_id', models.PositiveIntegerField()),
                ('is_pinned', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'note',
                'verbose_name_plural': 'notes',
            },
            bases=(models.Model,),
        ),
    ]

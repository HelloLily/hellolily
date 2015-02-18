# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaskStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'PENDING', max_length=20, db_index=True, choices=[(b'RECEIVED', b'RECEIVED'), (b'RETRY', b'RETRY'), (b'REVOKED', b'REVOKED'), (b'SUCCESS', b'SUCCESS'), (b'STARTED', b'STARTED'), (b'FAILURE', b'FAILURE'), (b'PENDING', b'PENDING')])),
                ('task_id', models.CharField(db_index=True, max_length=50, unique=True, null=True, blank=True)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Task statuses',
            },
            bases=(models.Model,),
        ),
    ]

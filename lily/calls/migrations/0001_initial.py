# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0003_tenant_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_id', models.CharField(max_length=40)),
                ('called_number', models.CharField(max_length=40)),
                ('caller_number', models.CharField(max_length=40)),
                ('internal_number', models.CharField(max_length=5)),
                ('status', models.IntegerField(max_length=10, choices=[(0, 'Ringing'), (1, 'Answered'), (2, 'Hung up')])),
                ('type', models.IntegerField(default=0, max_length=10, choices=[(0, 'Inbound'), (1, 'Outbound')])),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]

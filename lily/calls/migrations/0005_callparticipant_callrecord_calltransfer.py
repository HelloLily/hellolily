# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0005_tenant_billing'),
        ('calls', '0004_call_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name', blank=True)),
                ('number', models.CharField(max_length=40, verbose_name='Number')),
                ('internal_number', models.CharField(max_length=5, null=True, verbose_name='Interal number')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CallRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('call_id', models.CharField(unique=True, max_length=255, verbose_name='Unique call id')),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('end', models.DateTimeField(null=True, verbose_name='End')),
                ('status', models.PositiveSmallIntegerField(verbose_name='Status', choices=[(0, 'Ringing'), (1, 'In progress'), (2, 'Ended')])),
                ('direction', models.PositiveSmallIntegerField(verbose_name='Type', choices=[(0, 'Inbound'), (1, 'Outbound')])),
                ('caller', models.ForeignKey(related_name='calls_made', verbose_name='From', to='calls.CallParticipant')),
                ('destination', models.ForeignKey(related_name='calls_received', verbose_name='To', to='calls.CallParticipant', null=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CallTransfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(verbose_name='Timestamp')),
                ('call', models.ForeignKey(related_name='transfers', verbose_name='Call', to='calls.CallRecord')),
                ('destination', models.ForeignKey(related_name='transfers_received', verbose_name='To', to='calls.CallParticipant')),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

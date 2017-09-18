# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0005_tenant_billing'),
        ('deals', '0036_auto_20170419_0926'),
        ('integrations', '0004_migrate_integration_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.CharField(max_length=255)),
                ('document_status', models.CharField(max_length=255, null=True, blank=True)),
                ('extra_days', models.PositiveIntegerField(null=True, blank=True)),
                ('add_note', models.BooleanField(default=False)),
                ('next_step', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='deals.DealNextStep', null=True)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='deals.DealStatus', null=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='documentevent',
            unique_together=set([('tenant', 'event_type', 'document_status')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0001_initial'),
        ('tenant', '0001_initial'),
        ('parcels', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='contact',
            field=models.ForeignKey(verbose_name='contact', blank=True, to='contacts.Contact', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', verbose_name='created by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='case',
            name='parcel',
            field=models.ForeignKey(verbose_name='parcel', blank=True, to='parcels.Parcel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='case',
            name='status',
            field=models.ForeignKey(related_name='cases', verbose_name='status', to='cases.CaseStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='case',
            name='tenant',
            field=models.ForeignKey(to='tenant.Tenant', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='case',
            name='type',
            field=models.ForeignKey(related_name='cases', verbose_name='type', blank=True, to='cases.CaseType', null=True),
            preserve_default=True,
        ),
    ]

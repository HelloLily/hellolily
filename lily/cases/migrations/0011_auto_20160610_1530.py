# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import lily.utils.date_time


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0010_auto_20160510_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='account',
            field=models.ForeignKey(blank=True, to='accounts.Account', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='assigned_to',
            field=models.ForeignKey(related_name='assigned_cases', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='assigned_to_groups',
            field=models.ManyToManyField(related_name='assigned_to_groups', null=True, to='users.LilyGroup', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='contact',
            field=models.ForeignKey(blank=True, to='contacts.Contact', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(related_name='created_cases', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='expires',
            field=models.DateField(default=lily.utils.date_time.week_from_now),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='parcel',
            field=models.ForeignKey(blank=True, to='parcels.Parcel', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='priority',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Low'), (1, 'Medium'), (2, 'High'), (3, 'Critical')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='status',
            field=models.ForeignKey(related_name='cases', to='cases.CaseStatus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='subject',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='case',
            name='type',
            field=models.ForeignKey(related_name='cases', blank=True, to='cases.CaseType', null=True),
            preserve_default=True,
        ),
    ]

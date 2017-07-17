# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0019_auto_20170418_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.Account', null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='assigned_to',
            field=models.ForeignKey(related_name='assigned_cases', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contacts.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(related_name='created_cases', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='parcel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='parcels.Parcel', null=True),
        ),
    ]

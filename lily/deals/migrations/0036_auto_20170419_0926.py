# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0035_auto_20170314_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='assigned_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contacts.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='contacted_by',
            field=models.ForeignKey(related_name='deals', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='deals.DealContactedBy', null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='created_by',
            field=models.ForeignKey(related_name='created_deals', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='found_through',
            field=models.ForeignKey(related_name='deals', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='deals.DealFoundThrough', null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='why_customer',
            field=models.ForeignKey(related_name='deals', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='deals.DealWhyCustomer', null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='why_lost',
            field=models.ForeignKey(related_name='deals', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='deals.DealWhyLost', null=True),
        ),
    ]

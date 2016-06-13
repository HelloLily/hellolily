# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0027_auto_20160408_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='account',
            field=models.ForeignKey(to='accounts.Account'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_once',
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_recurring',
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='assigned_to',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='closed_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='contact',
            field=models.ForeignKey(blank=True, to='contacts.Contact', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='contacted_by',
            field=models.ForeignKey(related_name='deals', to='deals.DealContactedBy'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='created_by',
            field=models.ForeignKey(related_name='created_deals', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='currency',
            field=models.CharField(max_length=3, choices=[(b'EUR', 'Euro'), (b'GBP', 'British pound'), (b'USD', 'United States dollar'), (b'ZAR', 'South African rand'), (b'NOR', 'Norwegian krone'), (b'DKK', 'Danish krone'), (b'SEK', 'Swedish krone'), (b'CHF', 'Swiss franc')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='feedback_form_sent',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='found_through',
            field=models.ForeignKey(related_name='deals', to='deals.DealFoundThrough'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='import_id',
            field=models.CharField(default=b'', max_length=100, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='imported_from',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='is_checked',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='name',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='new_business',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='next_step',
            field=models.ForeignKey(related_name='deals', to='deals.DealNextStep'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='next_step_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='quote_id',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='status',
            field=models.ForeignKey(related_name='deals', to='deals.DealStatus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='why_customer',
            field=models.ForeignKey(related_name='deals', to='deals.DealWhyCustomer'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='why_lost',
            field=models.ForeignKey(related_name='deals', to='deals.DealWhyLost', null=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='deleted', editable=False, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('currency', models.CharField(default=b'EUR', max_length=3, verbose_name='currency', choices=[(b'EUR', 'Euro'), (b'GBP', 'British pound'), (b'NOR', 'Norwegian krone'), (b'DKK', 'Danish krone'), (b'SEK', 'Swedish krone'), (b'CHF', 'Swiss franc'), (b'USD', 'United States dollar')])),
                ('amount_once', models.DecimalField(verbose_name='one-time cost', max_digits=19, decimal_places=2)),
                ('amount_recurring', models.DecimalField(verbose_name='recurring costs', max_digits=19, decimal_places=2)),
                ('expected_closing_date', models.DateField(verbose_name='expected closing date')),
                ('closed_date', models.DateTimeField(null=True, verbose_name='closed date', blank=True)),
                ('stage', models.IntegerField(default=0, verbose_name='status', choices=[(0, 'Open'), (1, 'Proposal sent'), (2, 'Won'), (3, 'Lost'), (4, 'Called'), (5, 'Emailed')])),
                ('feedback_form_sent', models.BooleanField(default=False, verbose_name='feedback form sent', choices=[(False, 'No'), (True, 'Yes')])),
                ('new_business', models.BooleanField(default=False, verbose_name='new business', choices=[(False, 'No'), (True, 'Yes')])),
                ('account', models.ForeignKey(verbose_name='account', to='accounts.Account')),
                ('assigned_to', models.ForeignKey(verbose_name='assigned to', to=settings.AUTH_USER_MODEL)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'deal',
                'verbose_name_plural': 'deals',
            },
            bases=(models.Model,),
        ),
    ]

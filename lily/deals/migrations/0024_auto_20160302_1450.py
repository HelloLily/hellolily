# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from lily.tenant.models import Tenant


# Current hard coded values for the found us through field.
found_through_choices = [
    'Search engine',
    'Social media',
    'Talk with employee',
    'Existing customer',
    'Other',
    'Radio',
    'Public speaking',
    'Press and articles',
]


def create_found_through_entries(apps, schema_editor):
    DealFoundThrough = apps.get_model('deals', 'DealFoundThrough')
    Tenant = apps.get_model('tenant', 'Tenant')

    for tenant in Tenant.objects.all():
        for found_through_choice in found_through_choices:
            DealFoundThrough.objects.create(name=found_through_choice, tenant=tenant)


def link_found_through_entries(apps, schema_editor):
    Deal = apps.get_model('deals', 'Deal')
    DealFoundThrough = apps.get_model('deals', 'DealFoundThrough')

    deals = Deal.objects.all()

    for deal in deals:
        found_through_object = DealFoundThrough.objects.get(name=found_through_choices[deal.found_through], tenant=deal.tenant)
        deal.found_through = found_through_object.id
        deal.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('deals', '0023_auto_20160307_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealFoundThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('position', models.IntegerField(default=0, max_length=2)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(create_found_through_entries, do_nothing),
        migrations.RunPython(link_found_through_entries, do_nothing),
        migrations.AlterField(
            model_name='deal',
            name='found_through',
            field=models.ForeignKey(related_name='deals', verbose_name='found us through', to='deals.DealFoundThrough'),
            preserve_default=True,
        ),
    ]

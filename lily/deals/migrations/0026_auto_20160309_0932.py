# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# Current hard coded values for the status field.
status_choices = [
   'Open',
   'Proposal sent',
   'Won',
   'Lost',
   'Called',
   'Emailed',
]


def create_status_entries(apps, schema_editor):
    DealStatus = apps.get_model('deals', 'DealStatus')
    Tenant = apps.get_model('tenant', 'Tenant')

    for tenant in Tenant.objects.all():
        for status_choice in status_choices:
            DealStatus.objects.create(name=status_choice, tenant=tenant)


def link_status_entries(apps, schema_editor):
    Deal = apps.get_model('deals', 'Deal')
    DealStatus = apps.get_model('deals', 'DealStatus')

    deals = Deal.objects.all()

    for deal in deals:
        status_object = DealStatus.objects.get(name=status_choices[deal.stage], tenant=deal.tenant)
        deal.stage = status_object.id
        deal.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('deals', '0025_auto_20160308_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealStatus',
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
        migrations.RunPython(create_status_entries, do_nothing),
        migrations.RunPython(link_status_entries, do_nothing),
        migrations.AlterField(
            model_name='deal',
            name='stage',
            field=models.ForeignKey(related_name='deals', verbose_name='status', to='deals.DealStatus'),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='deal',
            old_name='stage',
            new_name='status',
        )
    ]



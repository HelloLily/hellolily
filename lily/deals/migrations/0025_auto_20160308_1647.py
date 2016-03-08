# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# Current hard coded values for the contacted by field.
contacted_by_choices = [
    'Quote',
    'Contact form',
    'Phone',
    'Web chat',
    'E-mail',
    'Instant connect',
    'Other',
]


def create_contacted_by_entries(apps, schema_editor):
    DealContactedBy = apps.get_model('deals', 'DealContactedBy')
    Tenant = apps.get_model('tenant', 'Tenant')

    for tenant in Tenant.objects.all():
        for contacted_by_choice in contacted_by_choices:
            DealContactedBy.objects.create(name=contacted_by_choice, tenant=tenant)


def link_contacted_by_entries(apps, schema_editor):
    Deal = apps.get_model('deals', 'Deal')
    DealContactedBy = apps.get_model('deals', 'DealContactedBy')

    deals = Deal.objects.all()

    for deal in deals:
        contacted_by_object = DealContactedBy.objects.get(name=contacted_by_choices[deal.contacted_by], tenant=deal.tenant)
        deal.contacted_by = contacted_by_object.id
        deal.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('deals', '0024_auto_20160302_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealContactedBy',
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
        migrations.RunPython(create_contacted_by_entries, do_nothing),
        migrations.RunPython(link_contacted_by_entries, do_nothing),
        migrations.AlterField(
            model_name='deal',
            name='contacted_by',
            field=models.ForeignKey(related_name='deals', verbose_name='contacted us by', to='deals.DealContactedBy'),
            preserve_default=True,
        ),
    ]

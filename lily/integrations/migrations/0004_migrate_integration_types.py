# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def increment_integration_type(apps, schema_editor):
    IntegrationDetails = apps.get_model('integrations', 'IntegrationDetails')

    details = IntegrationDetails.objects.all()

    for detail in details:
        detail.type += 1
        detail.save()


def decrement_integration_type(apps, schema_editor):
    IntegrationDetails = apps.get_model('integrations', 'IntegrationDetails')

    details = IntegrationDetails.objects.all()

    for detail in details:
        detail.type -= 1
        detail.save()


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0003_create_integration_types'),
    ]

    operations = [
        migrations.RunPython(increment_integration_type, decrement_integration_type),
        migrations.AlterField(
            model_name='integrationdetails',
            name='type',
            field=models.ForeignKey(related_name='details', to='integrations.IntegrationType'),
            preserve_default=True,
        ),
    ]

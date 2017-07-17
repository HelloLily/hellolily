# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Case = apps.get_model("cases", "Case")
    CaseType = apps.get_model("cases", "CaseType")

    for case in Case.objects.filter(type=None):
        case_type = CaseType.objects.get_or_create(
            tenant_id=case.tenant_id,
            name='Other'
        )[0]

        case.type = case_type
        case.save()


def backwards_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0017_auto_20161025_1359'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]

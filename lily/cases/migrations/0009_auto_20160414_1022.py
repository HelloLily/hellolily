# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def archive_closed_cases(apps, schema_editor):
    CaseStatus = apps.get_model('cases', 'CaseStatus')
    Case = apps.get_model('cases', 'Case')
    Tenant = apps.get_model('tenant', 'Tenant')

    tenant = Tenant.objects.get(pk=50)

    closed_status = CaseStatus.objects.get(status='Closed', tenant=tenant)

    for case in Case.objects.filter(status=closed_status, tenant=tenant, is_archived=False):
        case.is_archived = True
        case.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0008_auto_20160408_1519'),
    ]

    operations = [
         migrations.RunPython(archive_closed_cases, do_nothing),
    ]

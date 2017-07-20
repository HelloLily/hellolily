# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def remove_old_changes(apps, schema_editor):
    Change = apps.get_model('changes', 'Change')

    # Delete old change objects since they aren't up-to-date with the new format.
    Change.objects.all().delete()

def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('changes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_old_changes, do_nothing),
    ]

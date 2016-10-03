# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def merge_preposition(apps, schema_editor):
    Contact = apps.get_model('contacts', 'contact')

    for contact in Contact.objects.all():
        if contact.preposition:
            contact.last_name = ' '.join([contact.preposition, contact.last_name])
            contact.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0011_auto_20160922_1154'),
    ]

    operations = [
        migrations.RunPython(merge_preposition, do_nothing),
        migrations.RemoveField(
            model_name='contact',
            name='preposition',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def copy_raw_input(apps, schema_editor):
    PhoneNumber = apps.get_model('utils', 'PhoneNumber')

    for phone_number in PhoneNumber.objects.all():
        if phone_number.raw_input and phone_number.raw_input != phone_number.number:
            phone_number.number = phone_number.raw_input
            phone_number.save()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0008_externalapplink'),
    ]

    operations = [
        migrations.RunPython(copy_raw_input, do_nothing),
        migrations.RemoveField(
            model_name='phonenumber',
            name='raw_input',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def generalize_address_line(apps, schema_editor):
    Address = apps.get_model('utils', 'Address')

    addresses = Address.objects.all()
    for address in addresses:
        address.update_modified = False

        address_line = address.street
        if address.street_number:
            address_line += ' ' + str(address.street_number)
        if address.complement:
            if address.complement[:1].isdigit():
                address_line = address_line + ' - ' + address.complement
            else:
                address_line += address.complement

        address.address = address_line.strip()
        address.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0010_generalize_address_prepare'),
    ]

    operations = [
        migrations.RunPython(generalize_address_line),
    ]

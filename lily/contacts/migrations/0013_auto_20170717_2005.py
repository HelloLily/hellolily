# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0012_remove_contact_preposition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='function',
            name='manager',
            field=models.ForeignKey(related_name='manager', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contacts.Contact', null=True),
        ),
    ]

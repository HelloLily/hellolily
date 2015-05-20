# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_primary_emails(apps, schema_editor):
    # We can't import the EmailAddress model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    EmailAddress = apps.get_model('utils', 'EmailAddress')
    for email_address in EmailAddress.objects.all():
        if email_address.is_primary and email_address.status != 0:
            email_address.status = 2
            email_address.save()

class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0003_auto_20150420_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='status',
            field=models.IntegerField(default=1, max_length=50, verbose_name='status', choices=[(2, 'Primary'), (1, 'Other'), (0, 'Inactive')]),
            preserve_default=True,
        ),
        migrations.RunPython(set_primary_emails),

    ]

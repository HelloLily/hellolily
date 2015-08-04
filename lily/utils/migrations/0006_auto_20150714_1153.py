# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0005_remove_emailaddress_is_primary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historylistitem',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_utils.historylistitem_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]

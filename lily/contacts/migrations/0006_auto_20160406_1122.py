# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.contacts.models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20150527_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='picture',
            field=models.ImageField(upload_to=lily.contacts.models.get_contact_picture_upload_path, verbose_name='picture', blank=True),
            preserve_default=True,
        ),
    ]

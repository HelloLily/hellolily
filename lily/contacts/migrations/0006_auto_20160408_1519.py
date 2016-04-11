# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lily.contacts.models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20150527_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='deleted',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='picture',
            field=models.ImageField(upload_to=lily.contacts.models.get_contact_picture_upload_path, verbose_name='picture', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='deleted',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='function',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
            preserve_default=True,
        ),
    ]

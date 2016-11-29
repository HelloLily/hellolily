# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0009_remove_polymorphic_data_migrate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='NewNote',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')
        ),
        migrations.AlterField(
            model_name='NewNote',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')
        ),
        migrations.DeleteModel('Note'),
        migrations.RenameModel('NewNote', 'Note')
    ]

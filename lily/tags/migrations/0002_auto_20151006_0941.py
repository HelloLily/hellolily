# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def tag_names_to_lowercase(apps, schema_editor):
    """
    Clean up the tag table by:
        - Removing tags with an empty name.
        - Rename all uppercase names to lowercase
    """
    Tag = apps.get_model('tags', 'Tag')
    # First remove empty string name tags.
    Tag.objects.filter(name='').delete()

    # Then move all names to lowercase.
    for tag in Tag.objects.all():
        tag.name = tag.name.lower()
        try:
            tag.save()
        except Tag.IntegrityError:
            tag.delete()


def noop_rollback(apps, schema_editor):
    """
    No rollback function. Used to test migration with.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(tag_names_to_lowercase, noop_rollback),
    ]

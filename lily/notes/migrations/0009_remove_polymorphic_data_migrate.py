# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.models import ContentType

# Trigger migrations for Travis testing.


def forwards(apps, schema_editor):

    OldNote = apps.get_model('notes', 'Note')
    NewNote = apps.get_model('notes', 'NewNote')

    for old_note in OldNote.objects.all():
        note = NewNote(pk=old_note.pk,
                       tenant=old_note.tenant,
                       content=old_note.content,
                       author=old_note.author,
                       type=old_note.type,
                       content_type=old_note.content_type,
                       object_id=old_note.object_id,
                       is_pinned=old_note.is_pinned,
                       deleted=old_note.deleted,
                       is_deleted=old_note.is_deleted,
                       created=old_note.sort_by_date,
                       modified=old_note.modified
                       )
        note.save()
        note.update_modified = False
        note.created = old_note.sort_by_date
        note.modified = old_note.modified
        note.save()


def reverse(apps, schema_editor):
    OldNote = apps.get_model('notes', 'Note')
    NewNote = apps.get_model('notes', 'NewNote')

    for new_note in NewNote.objects.all():
        note = OldNote(pk=new_note.pk,
                       tenant=new_note.tenant,
                       content=new_note.content,
                       author=new_note.author,
                       type=new_note.type,
                       content_type=new_note.content_type,
                       object_id=new_note.object_id,
                       is_pinned=new_note.is_pinned,
                       deleted=new_note.deleted,
                       is_deleted=new_note.is_deleted,
                       sort_by_date=new_note.created,
                       modified=new_note.modified
                       )
        note.save()
        ctype = ContentType.objects.get_for_model(OldNote)
        note.polymorphic_ctype_id = ctype
        note.update_modified = False
        note.modified = new_note.modified
        note.save()


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0008_remove_polymorphic_prepare'),
        ('users', '0011_remove_lilyuser_preposition')
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
        migrations.RunSQL(
            "SELECT setval('notes_newnote_id_seq', (SELECT MAX(id) FROM notes_newnote))",
            "SELECT setval('utils_historylistitem_id_seq', (SELECT MAX(id) FROM notes_newnote))",
        )
    ]

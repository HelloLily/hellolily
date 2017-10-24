# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

import logging

from django.db import migrations, models


logger = logging.getLogger(__name__)


ENDED = 2
INBOUND = 0


def migrate_calls(apps, schema_editor):
    Call = apps.get_model('calls', 'Call')
    CallRecord = apps.get_model('calls', 'CallRecord')
    CallParticipant = apps.get_model('calls', 'CallParticipant')
    Note = apps.get_model('notes', 'Note')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    call_ctype = ContentType.objects.get_for_model(Call)
    cr_ctype = ContentType.objects.get_for_model(CallRecord)

    calls = Call.objects.filter(created__isnull=False)

    for index, call in enumerate(calls):
        caller = CallParticipant.objects.get_or_create(
            tenant=call.tenant,
            name=call.caller_name,
            number=call.caller_number,
            internal_number=None
        )[0]

        destination = CallParticipant.objects.get_or_create(
            tenant=call.tenant,
            name='',
            number=call.called_number,
            internal_number=call.internal_number
        )[0]

        unique_id = call.unique_id
        call_id_exists = CallRecord.objects.filter(call_id=unique_id).exists()
        while call_id_exists:
            unique_id = ''.join(random.choice(string.lowercase) for x in range(100))
            call_id_exists = CallRecord.objects.filter(call_id=unique_id).exists()

        cr = CallRecord.objects.create(
            tenant=call.tenant,
            call_id=unique_id,
            start=call.created,
            end=None,
            status=ENDED,
            direction=INBOUND,
            caller=caller,
            destination=destination
        )

        for note in Note.objects.filter(content_type=call_ctype, object_id=call.id):
            Note.objects.create(
                tenant_id=note.tenant_id,
                content=note.content,
                author_id=note.author_id,
                type=note.type,
                is_pinned=note.is_pinned,
                content_type=cr_ctype,
                object_id=cr.id
            )


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0005_callparticipant_callrecord_calltransfer'),
        ('notes', '0011_auto_20161125_1559'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(migrate_calls, do_nothing),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


ENDED = 2
INBOUND = 0


def migrate_calls(apps, schema_editor):
    Call = apps.get_model('calls', 'Call')
    CallRecord = apps.get_model('calls', 'CallRecord')
    CallParticipant = apps.get_model('calls', 'CallParticipant')
    LilyUser = apps.get_model('users', 'LilyUser')
    Contact = apps.get_model('contacts', 'Contact')
    Account = apps.get_model('accounts', 'Account')

    for call in Call.objects.all():
        caller = CallParticipant.objects.get_or_create(
            tenant=call.tenant,
            name=call.caller_name,
            number=call.caller_number,
            internal_number=None
        )[0]

        destination_name = ''
        user = LilyUser.objects.filter(internal_number=call.internal_number).first()
        if user:
            destination_name = u' '.join([user.first_name, user.last_name]).strip()
        else:
            contact = Contact.objects.filter(phone_numbers__number=call.called_number).first()

            if contact:
                destination_name = ' '.join([contact.first_name, contact.last_name]).strip()
            else:
                account = Account.objects.filter(phone_numbers__number=call.called_number).first()

                if account:
                    destination_name = account.name

        destination = CallParticipant.objects.get_or_create(
            tenant=call.tenant,
            name=destination_name,
            number=call.called_number,
            internal_number=call.internal_number
        )[0]

        CallRecord.objects.create(
            tenant=call.tenant,
            call_id=call.unique_id,
            start=call.created,
            end=None,
            status=ENDED,
            direction=INBOUND,
            caller=caller,
            destination=destination
        )


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0005_callparticipant_callrecord_calltransfer'),
        ('users', '0023_userinvite'),
        ('contacts', '0013_auto_20170717_2005'),
        ('accounts', '0019_auto_20170419_0926'),
    ]

    operations = [
        migrations.RunPython(migrate_calls, do_nothing),
    ]

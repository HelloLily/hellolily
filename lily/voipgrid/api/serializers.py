import json
import logging
from copy import copy

from channels import Group
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework import serializers

from lily.accounts.models import Account
from lily.calls.models import CallRecord, CallParticipant, CallTransfer
from lily.contacts.models import Contact
from lily.users.models import LilyUser


logger = logging.getLogger(__name__)


class CallNotificationSerializer(serializers.Serializer):
    call_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=('ringing', 'in-progress', 'ended', 'transfer', ))
    direction = serializers.ChoiceField(choices=('inbound', 'outbound', ))

    # For ringing, in-progress and ended events.
    caller = serializers.DictField(required=False)
    destination = serializers.DictField(required=False)

    # For transfer events.
    party1 = serializers.DictField(required=False)
    party2 = serializers.DictField(required=False)
    redirector = serializers.DictField(required=False)
    merged_id = serializers.CharField(required=False)

    def to_representation(self, instance):
        # Because the CallRecord model doesn't have the same fields DRF will complain when returning the object.
        # We don't need to return an object after creation because VG doesn't care.
        return {}

    def create(self, validated_data):
        destination = validated_data.get('destination', {})

        if destination and not destination.get('number', '').startswith('+'):
            # We don't save phone calls to internal numbers because:
            # - They aren't visible anywhere.
            # - They are temporary phonecalls when a user transfers the call.
            return CallRecord()

        save_func = getattr(self, 'save_{}'.format(validated_data['status'].replace('-', '_')))

        return save_func(validated_data)

    def save_participant(self, data, metadata=False):
        name = data.get('name', '') or ''
        number = data.get('number', '') or ''

        try:
            internal_number = data['user_numbers'][0]
        except IndexError:
            internal_number = None

        # First try to autocomplete the name using a user.
        if internal_number and not name:
            user = LilyUser.objects.filter(internal_number=internal_number).first()
            if user:
                name = user.full_name

        meta = {
            'destination': 'create',
            'icon': static('app/images/notification_icons/add-account.png'),
            'params': {
                'name': name,
                'number': number,
            },
        }

        # Second try to autocomplete the name using a contact.
        if number and not name:
            contact = Contact.objects.filter(phone_numbers__number=number).first()

            if contact:
                name = contact.full_name
                meta = {
                    'destination': 'contact',
                    'icon': static('app/images/notification_icons/contact.png'),
                    'params': {
                        'name': name,
                        'number': number,
                        'id': contact.id,
                    },
                }

        # Third try to autocomplete the name using an account.
        if number and not name:
            account = Account.objects.filter(phone_numbers__number=number).first()

            if account:
                name = account.name
                meta = {
                    'destination': 'account',
                    'icon': static('app/images/notification_icons/account.png'),
                    'params': {
                        'name': name,
                        'number': number,
                        'id': account.id,
                    },
                }

        participant = CallParticipant.objects.get_or_create(
            name=name,
            number=number,
            internal_number=internal_number
        )[0]

        if metadata:
            return participant, meta

        return participant

    def save_ringing(self, data):
        caller, caller_meta = self.save_participant(data['caller'], metadata=True)
        destination = data['destination']

        data.update({
            'start': data.pop('timestamp'),
            'caller': caller,
            'destination': None,  # During ringing we don't want to store destination yet, only when it's picked up.
            'status': CallRecord.RINGING,
            'direction': CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
        })
        cr = CallRecord.objects.get_or_create(**data)[0]

        user_list = LilyUser.objects.filter(internal_number__in=destination['user_numbers'])
        for user in user_list:
            # Sends the data as a notification event to the users.
            Group('user-%s' % user.id).send({
                'text': json.dumps({
                    'event': 'notification',
                    'data': caller_meta
                }),
            })

        return cr

    def save_in_progress(self, data):
        try:
            cr = CallRecord.objects.get(call_id=data['call_id'])
        except CallRecord.DoesNotExist:
            logger.exception('Unexpected in-progress notification for call {}'.format(data['call_id']))
            return CallRecord()

        updated_data = {
            'destination': self.save_participant(data['destination']),
            'status': CallRecord.IN_PROGRESS,
        }

        for attr, value in updated_data.items():
            setattr(cr, attr, value)
        cr.save()

        return cr

    def save_transfer(self, data):
        crs = CallRecord.objects.filter(
            call_id=data['call_id']
        ) or CallRecord.objects.filter(
            call_id=data['merged_id']
        )

        if not crs:
            return CallRecord()

        CallTransfer.objects.create(**{
            'timestamp': data['timestamp'],
            'call': crs[0],
            'destination': self.save_participant(data['party2']),
        })

        return crs[0]

    def save_ended(self, data):
        try:
            cr = CallRecord.objects.get(call_id=data['call_id'])
        except CallRecord.DoesNotExist:
            # This can happen if the destination is unavailable. Then you get the ended notification right away.
            # Use the save ringing to create the cr and immediately overwrite the data afterwards.
            cr = self.save_ringing(copy(data))

        updated_data = {
            'end': data.pop('timestamp'),
            'status': CallRecord.ENDED,
        }

        for attr, value in updated_data.items():
            setattr(cr, attr, value)
        cr.save()

        return cr

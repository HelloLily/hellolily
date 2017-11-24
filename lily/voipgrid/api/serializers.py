import json
import logging
from copy import copy

from channels import Group
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.models import Account
from lily.calls.models import CallRecord, CallParticipant, CallTransfer
from lily.contacts.models import Contact
from lily.users.models import LilyUser

logger = logging.getLogger(__name__)


def create_or_get(model_cls, lookup, data):
    """
    This function assumes that you have a unique field in the model class.
    The unique field will raise an IntegrityError if there is an existing record already.
    """
    try:
        return model_cls.objects.create(**data)
    except IntegrityError as e:
        logger.warning('create_or_get IntegrityError: {}'.format(''.join(e.message.splitlines())))
        return model_cls.objects.get(**lookup)


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
        internal_number = data.get('account_number', '') or ''

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
        cr = create_or_get(CallRecord, lookup={'call_id': data['call_id']}, data=data)

        user_list = LilyUser.objects.filter(internal_number=destination['account_number'])
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


class CallNotificationV2Serializer(serializers.Serializer):
    call_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=('ringing', 'in-progress', 'ended', 'warm-transfer', 'cold-transfer', ))
    direction = serializers.ChoiceField(choices=('inbound', 'outbound', ))
    caller = serializers.DictField()
    destination = serializers.DictField()

    # For transfer events.
    merged_id = serializers.CharField(required=False)
    redirector = serializers.DictField(required=False)

    def to_representation(self, instance):
        # Because the CallRecord model doesn't have the same fields DRF will complain when returning the object.
        # We don't need to return an object after creation because VG doesn't care.
        return {}

    def validate(self, data):
        if data['status'] in ['warm-transfer', 'cold-transfer', ]:
            merged_id = data.get('merged_id')
            redirector = data.get('redirector')

            if not merged_id and not redirector:
                raise serializers.ValidationError({
                    'merged_id': _('This field is required.'),
                    'redirector': _('This field is required.'),
                })
            elif not merged_id:
                raise serializers.ValidationError({
                    'merged_id': _('This field is required.'),
                })
            elif not redirector:
                raise serializers.ValidationError({
                    'redirector': _('This field is required.'),
                })

        return data

    def create(self, validated_data):
        caller = validated_data['caller']

        if caller and not caller.get('number', '').startswith('+'):
            # We don't save phone calls from internal numbers because:
            # - They aren't visible anywhere.
            # - They are temporary phone calls when a user transfers the call.
            # - They are just a simple call between colleagues.
            return CallRecord()

        # Get the correct save function for the status type, e.g. status: in-progress will become save_in_progress.
        save_func = getattr(self, 'save_{}'.format(validated_data['status'].replace('-', '_')))

        logger.info(
            'Now saving call_id: "{}" using function {}.'.format(
                validated_data['call_id'],
                save_func.__name__
            )
        )

        return save_func(validated_data)

    def send_notification(self, internal_numbers, participant, source):
        data = {
            'destination': 'create',
            'icon': static('app/images/notification_icons/add-account.png'),
            'params': {
                'name': participant.name,
                'number': participant.number,
            },
        }

        if isinstance(source, Account):
            data = {
                'destination': 'account',
                'icon': static('app/images/notification_icons/account.png'),
                'params': {
                    'name': participant.name,
                    'number': participant.number,
                    'id': source.id,
                },
            }
        elif isinstance(source, Contact):
            data = {
                'destination': 'contact',
                'icon': static('app/images/notification_icons/contact.png'),
                'params': {
                    'name': participant.name,
                    'number': participant.number,
                    'id': source.id,
                },
            }

        user_list = LilyUser.objects.filter(internal_number__in=internal_numbers)
        for user in user_list:
            # Sends the data as a notification event to the users.
            Group('user-{}'.format(user.id)).send({
                'text': json.dumps({
                    'event': 'notification',
                    'data': data
                }),
            })

    def save_participant(self, data):
        number = data['number'] or ''
        name = ''
        source = None

        # Order of saving internal number for participant:
        # 1 - user_numbers, if multiple use the first one.
        # 2 - account_number.
        # 3 - empty string.
        if data['user_numbers']:
            internal_number = data['user_numbers'][0]
        elif data['account_number']:
            internal_number = data['account_number']
        else:
            internal_number = ''

        # Order of saving the name for participant:
        # 1 - based on a user, if multiple the one that last logged in.
        # 2 - based on a contact, if multiple the one that was last modified.
        # 3 - based on an account, if multiple the one that was last modified.
        # 4 - use the vg provided one as a backup.
        if internal_number:
            user = LilyUser.objects.filter(internal_number=internal_number).order_by('-last_login').first()
            if user:
                name = user.full_name
                source = user

        if number and not name:
            contact = Contact.objects.filter(phone_numbers__number=number).order_by('-modified').first()

            if contact:
                name = contact.full_name
                source = contact
            else:
                account = Account.objects.filter(phone_numbers__number=number).order_by('-modified').first()

                if account:
                    name = account.name
                    source = account

        participant = CallParticipant.objects.get_or_create(
            name=name or data['name'] or '',
            number=number,
            internal_number=internal_number
        )[0]

        return participant, source

    def save_ringing(self, data):
        caller, source = self.save_participant(data['caller'])
        internal_numbers = set()
        for target in data['destination']['targets']:
            internal_numbers.update(target['user_numbers'])
            if target['account_number']:
                internal_numbers.add(str(target['account_number']))

        data.update({
            'start': data.pop('timestamp'),
            'caller': caller,
            'destination': None,  # During ringing we don't want to store destination yet, only when it's picked up.
            'status': CallRecord.RINGING,
            'direction': CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
        })
        cr = CallRecord.objects.get_or_create(call_id=data['call_id'], defaults=data)[0]

        self.send_notification(internal_numbers, caller, source)

        return cr

    def save_in_progress(self, data):
        cr = CallRecord.objects.get(call_id=data['call_id'])
        last_transfer = cr.transfers.order_by('timestamp').last()

        if last_transfer and not last_transfer.destination:
            last_transfer.destination = self.save_participant(data['destination']['target'])[0]
            last_transfer.save()
        else:
            updated_data = {
                'destination': self.save_participant(data['destination']['target'])[0],
                'status': CallRecord.IN_PROGRESS,
            }

            for attr, value in updated_data.items():
                setattr(cr, attr, value)
            cr.save()

        return cr

    def save_warm_transfer(self, data):
        try:
            cr = CallRecord.objects.get(call_id=data['call_id'])
        except CallRecord.DoesNotExist:
            # If the call with call_id does not exist try the merged_id, if that one does exist, switch the ids around.
            cr = CallRecord.objects.get(call_id=data['merged_id'])
            cr.call_id = data['call_id']
            cr.save()

        CallTransfer.objects.create(
            timestamp=data['timestamp'],
            call=cr,
            destination=self.save_participant(data['destination']['target'])[0]
        )

        return cr

    def save_cold_transfer(self, data):
        try:
            cr = CallRecord.objects.get(call_id=data['call_id'])
        except CallRecord.DoesNotExist:
            # If the call with call_id does not exist try the merged_id, if that one does exist, switch the ids around.
            cr = CallRecord.objects.get(call_id=data['merged_id'])
            cr.call_id = data['call_id']
            cr.save()

        CallTransfer.objects.create(
            timestamp=data['timestamp'],
            call=cr,
            destination=None
        )

        return cr

    def save_ended(self, data):
        try:
            cr = CallRecord.objects.get(call_id=data['call_id'])
            last_transfer = cr.transfers.order_by('timestamp').last()

            if last_transfer and not last_transfer.destination:
                last_transfer.delete()

            updated_data = {
                'end': data.pop('timestamp'),
                'status': CallRecord.ENDED,
            }

            for attr, value in updated_data.items():
                setattr(cr, attr, value)
            cr.save()
        except CallRecord.DoesNotExist:
            # This can happen if the destination is unavailable. Then you get the ended notification right away.
            caller, source = self.save_participant(data['caller'])
            data.update({
                'start': data['timestamp'],
                'end': data.pop('timestamp'),  # Pop it to prevent error of unknown field on model during save.
                'caller': caller,
                'destination': None,  # During ringing we don't want to store destination, only when it's picked up.
                'status': CallRecord.ENDED,
                'direction': CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
            })
            cr = CallRecord.objects.get_or_create(**data)[0]

        return cr

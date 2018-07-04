import json
import logging

from channels import Group
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.models import Account
from lily.calls.models import CallRecord, CallParticipant, CallTransfer
from lily.contacts.models import Contact
from lily.users.models import LilyUser


logger = logging.getLogger(__name__)
# For now outbound call integration is limted to VoIPGRID, Voys, Voys SA, Lily, Firm24, LegalThings,
# Converdis B.V, Converdis
OUTBOUND_ENABLED_TENANTS = [10, 50, 52, 130, 300, 534, 601, 613]


class CallNotificationSerializer(serializers.Serializer):
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
        destination = validated_data['destination']
        tenant = self.context['request'].user.tenant

        if validated_data['direction'] == 'outbound':
            if tenant.id not in OUTBOUND_ENABLED_TENANTS:
                # For now we want to enable outbound call integration only for selected tenants to test the feature.
                return CallRecord()
            data = self.match_external_participant(destination)
            if not data['source']:
                # We don't save outbound calls where the destination isn't an account or a contact.
                # This is the only reliable way to filter out internal calls.
                return CallRecord()

        # Get the correct save function for the status type, e.g. status: in-progress will become save_in_progress.
        save_func = getattr(self, 'save_{}'.format(validated_data['status'].replace('-', '_')))

        logger.info(
            'Now saving call_id: "{}" using function {}.'.format(
                validated_data['call_id'],
                save_func.__name__
            )
        )

        result = save_func(validated_data)

        logger.info(
            'Done saving call_id: "{}" using function {}.'.format(
                validated_data['call_id'],
                save_func.__name__
            )
        )

        return result

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

    def get_target_internal_numbers(self, target):
        internal_numbers = set()

        internal_numbers.update(target['user_numbers'])
        if target['account_number']:
            internal_numbers.add(str(target['account_number']))

        return list(internal_numbers)

    def match_internal_participant(self, data):
        name = ''
        number = data['number'] or ''
        internal_number = ''
        source = None

        internal_number_list = self.get_target_internal_numbers(data)

        if internal_number_list:
            user = LilyUser.objects.filter(
                internal_number__in=internal_number_list,
                is_active=True
            ).order_by('-last_login').first()

            if user:
                name = user.full_name
                internal_number = user.internal_number
                source = user
            else:
                # If there was no user found with one of the internal numbers, just use first from the list.
                internal_number = internal_number_list[0]

        if not name:
            name = self.context['request'].user.tenant.name

        return {
            'name': name,
            'number': number,
            'internal_number': internal_number,
            'source': source,
        }

    def match_external_participant(self, data):
        name = ''
        number = data['number'] or ''
        source = None

        contact = Contact.objects.filter(
            phone_numbers__number=number,
            is_deleted=False
        ).order_by('-modified').first()

        if contact:
            name = contact.full_name
            source = contact
        else:
            account = Account.objects.filter(
                phone_numbers__number=number,
                is_deleted=False
            ).order_by('-modified').first()

            if account:
                name = account.name
                source = account

        return {
            'name': name,
            'number': number,
            'internal_number': '',
            'source': source,
        }

    def save_caller(self, direction, caller):
        """
        Save the caller of a conversation.
        It depends on the direction of the call if the caller is the internal or external party.

        Inbound: caller is the external party -> match to contacts/accounts, fallback to the voipgrid name.
        Outbound: caller is the internal party -> match to users, fallback to the tenant name.
        """
        if direction == 'inbound':
            data = self.match_external_participant(caller)
        else:  # direction == outbound
            data = self.match_internal_participant(caller)

        participant = CallParticipant.objects.get_or_create(
            name=data['name'],
            number=data['number'],
            internal_number=data['internal_number']
        )[0]

        return participant, data['source']

    def save_destination(self, direction, destination):
        """
        Save the destination of a conversation.
        It depends on the direction of the call if the destination is the internal or external party.

        Inbound: destination is the internal party -> match to users, fallback to the tenant name.
        Outbound: destination is the external party -> match to contacts/accounts, fallback to the voipgrid name.
        """
        # Get the target out of the destination, but use the main destination number.
        # We use the main number because target numbers can be dial templates or callgroup ids and stuff.
        target = destination['target']

        if not target['number'].startswith('+'):
            # The target number may be internal due to call forwarding.
            # If so, the destination number is probably the number that was called.
            target['number'] = destination['number']

        if direction == 'inbound':
            data = self.match_internal_participant(target)
        else:  # direction == outbound
            data = self.match_external_participant(target)

        participant = CallParticipant.objects.get_or_create(
            name=data['name'],
            number=data['number'],
            internal_number=data['internal_number']
        )[0]

        return participant

    def save_ringing(self, data):
        caller, source = self.save_caller(direction=data['direction'], caller=data['caller'])

        cr = CallRecord.objects.get_or_create(call_id=data['call_id'], defaults={
            'call_id': data['call_id'],
            'start': data['timestamp'],
            'end': None,
            'status': CallRecord.RINGING,
            'direction': CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
            'caller': caller,
            'destination': None,  # During ringing we don't want to store destination yet, only when it's picked up.
        })[0]

        if data['direction'] == 'inbound':
            # Only send notifications for incoming calls.
            internal_numbers = list()
            for target in data['destination']['targets']:
                internal_numbers += self.get_target_internal_numbers(target)

            self.send_notification(internal_numbers, caller, source)

        return cr

    def save_in_progress(self, data):
        try:
            cr = CallRecord.objects.get(call_id=data['call_id'])
            last_transfer = cr.transfers.order_by('timestamp').last()

            if last_transfer and not last_transfer.destination:
                last_transfer.destination = self.save_destination(
                    direction=data['direction'],
                    destination=data['destination']
                )

                last_transfer.save()
            else:
                updated_data = {
                    'destination': self.save_destination(direction=data['direction'], destination=data['destination']),
                    'status': CallRecord.IN_PROGRESS,
                }

                for attr, value in updated_data.items():
                    setattr(cr, attr, value)
                cr.save()
        except CallRecord.DoesNotExist:
            caller, source = self.save_caller(direction=data['direction'], caller=data['caller'])
            destination = self.save_destination(direction=data['direction'], destination=data['destination'])

            cr = CallRecord.objects.create(
                call_id=data['call_id'],
                start=data['timestamp'],
                end=None,
                status=CallRecord.IN_PROGRESS,
                direction=CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
                caller=caller,
                destination=destination
            )

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
            destination=self.save_destination(direction=data['direction'], destination=data['destination'])
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
            caller, source = self.save_caller(direction=data['direction'], caller=data['caller'])

            data.update({
                'start': data['timestamp'],
                'end': data.pop('timestamp'),  # Pop it to prevent error of unknown field on model during save.
                'caller': caller,
                'destination': None,
                'status': CallRecord.ENDED,
                'direction': CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
            })
            cr = CallRecord.objects.get_or_create(**data)[0]

        return cr

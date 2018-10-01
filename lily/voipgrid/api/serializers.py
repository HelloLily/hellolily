import json
import logging
import traceback

from channels import Group
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.models import Account
from lily.calls.models import CallRecord, CallParticipant, CallTransfer
from lily.contacts.models import Contact
from lily.users.models import LilyUser
from lily.utils.functions import get_country_code_by_country, get_phone_number_without_country_code

import phonenumbers
from phonenumbers import geocoder, NumberParseException


logger = logging.getLogger(__name__)


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
        caller = validated_data['caller']
        destination = validated_data['destination']

        if validated_data['direction'] == 'outbound':

            # Because of GRID-4965, the API returns the destination number in the same format user inserted it,
            # so if country code is missing let's patch it with the one from the caller number.
            if not destination['number'].startswith('+'):
                if caller['number'].startswith('+'):
                    try:
                        caller_number = phonenumbers.parse(caller['number'], None)
                        country_code = get_country_code_by_country(
                            geocoder.country_name_for_number(caller_number, 'en')
                        )
                        destination_number = phonenumbers.parse(destination['number'], country_code)

                        if phonenumbers.is_valid_number(destination_number):
                            destination['number'] = phonenumbers.format_number(
                                destination_number,
                                phonenumbers.PhoneNumberFormat.E164
                            )

                    except NumberParseException, e:
                        logger.error(traceback.format_exc(e))

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
        user = None

        # First try to find a matching user with internal number.
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

        # Many users do not have their internal number set in Lily. In this case try with the phone_number field.
        if not name:
            if number:
                # Only use the returned user if there was one exact match, otherwise it's probably a company number.
                try:
                    user = LilyUser.objects.get(
                        phone_number=number,
                        is_active=True,
                    )
                except (LilyUser.MultipleObjectsReturned, LilyUser.DoesNotExist):
                    pass
                # And in Lily the phone number can also be in national format, search also with that
                if not user:
                    try:
                        user = LilyUser.objects.get(
                            phone_number__endswith=get_phone_number_without_country_code(number),
                            is_active=True,
                        )
                    except (LilyUser.MultipleObjectsReturned, LilyUser.DoesNotExist):
                        pass
                if user:
                    name = user.full_name
                    if user.internal_number:
                        internal_number = user.internal_number
                    source = user

        # And if there is no match with internal_number or phone_number, just use the tenant name.
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
        if direction == 'inbound':
            target = destination['target']
        # For outbound calls we want to save the destination already at ringing stage.
        # Target isn't then defined yet so let's create one based on the destination number.
        else:  # direction == outbound
            target = {
                'user_numbers': [],
                'number': destination['number'],
                'account_number': None,
                'name': '',
            }

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

        # For inbound calls we wan't to store the destination only when the call is picked up.
        if data['direction'] == 'inbound':
            destination = None
        else:   # For outbound calls we can and want to save the destination already now.
            destination = self.save_destination(direction=data['direction'], destination=data['destination'])

        cr = CallRecord.objects.get_or_create(call_id=data['call_id'], defaults={
            'call_id': data['call_id'],
            'start': data['timestamp'],
            'end': None,
            'status': CallRecord.RINGING,
            'direction': CallRecord.INBOUND if data['direction'] == 'inbound' else CallRecord.OUTBOUND,
            'caller': caller,
            'destination': destination,
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
            elif data['direction'] == 'inbound':
                destination = self.save_destination(direction=data['direction'], destination=data['destination'])
                cr.destination = destination
                cr.status = CallRecord.IN_PROGRESS
                cr.save()
            else:  # For outbound calls the destination has been saved already in ringing stage.
                cr.status = CallRecord.IN_PROGRESS
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

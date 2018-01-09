from random import randrange

from copy import deepcopy
from django.utils import timezone
from faker.factory import Factory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from lily.calls.models import CallRecord
from lily.tests.utils import UserBasedTest


faker = Factory.create('nl_NL')


class CallNotificationsAPITestCase(UserBasedTest, APITestCase):
    list_url = 'callnotification-list'
    detail_url = 'callnotification-detail'

    def generate_number(self, internal=False):
        if internal:
            return str(randrange(100, 999))

        return '+3150{}'.format(randrange(1000000, 9999999))  # Random int of length 7.

    def generate_participant(self, number=None, internal=False):
        return {
            'account_number': randrange(100, 999) if internal else None,
            'user_numbers': [str(randrange(100, 999)), ] if internal else [],
            'number': number or self.generate_number(),
            'name': faker.name(),
        }

    def generate_destination(self, number=None, targets=None):
        if not number:
            number = self.generate_number()

        return {
            'number': number,
            'targets': targets or [
                self.generate_participant(number, True),
            ]
        }

    def generate_ringing_json(self, call_id, caller=None, destination=None):
        return {
            'call_id': '24c562241e9f-1502721212.{}'.format(call_id),
            'timestamp': timezone.now().isoformat(),
            'status': 'ringing',
            'version': 'v2',
            'direction': 'inbound',
            'caller': caller or self.generate_participant(),
            'destination': destination or self.generate_destination(),
        }

    def generate_in_progress_json(self, call_id, caller=None, target=None):
        if not target:
            target = self.generate_participant()

        return {
            'call_id': '24c562241e9f-1502721212.{}'.format(call_id),
            'timestamp': timezone.now().isoformat(),
            'status': 'in-progress',
            'version': 'v2',
            'direction': 'inbound',
            'caller': caller or self.generate_participant(),
            'destination': {
                'number': target['number'],
                'target': target,
            },
        }

    def generate_warm_transfer_json(self, call_id, merged_id, caller=None, target=None, redirector=None):
        if not target:
            target = self.generate_participant()

        return {
            'call_id': '24c562241e9f-1502721212.{}'.format(call_id),
            'merged_id': '24c562241e9f-1502721212.{}'.format(merged_id),
            'timestamp': timezone.now().isoformat(),
            'status': 'warm-transfer',
            'version': 'v2',
            'direction': 'inbound',
            'caller': caller or self.generate_participant(),
            'destination': {
                'number': target['number'],
                'target': target,
            },
            'redirector': redirector or self.generate_participant(),
        }

    def generate_cold_transfer_json(self, call_id, merged_id, caller=None, destination=None, redirector=None):
        return {
            'call_id': '24c562241e9f-1502721212.{}'.format(call_id),
            'merged_id': '24c562241e9f-1502721212.{}'.format(merged_id),
            'timestamp': timezone.now().isoformat(),
            'status': 'cold-transfer',
            'version': 'v2',
            'direction': 'inbound',
            'caller': caller or self.generate_participant(),
            'destination': destination or self.generate_destination(),
            'redirector': redirector or self.generate_participant(),
        }

    def generate_ended_json(self, call_id, reason='completed', caller=None, number=None):
        if not number:
            number = self.generate_participant()['number']

        return {
            'call_id': '24c562241e9f-1502721212.{}'.format(call_id),
            'timestamp': timezone.now().isoformat(),
            'status': 'ended',
            'reason': reason,
            'version': 'v2',
            'direction': 'inbound',
            'caller': caller or self.generate_participant(),
            'destination': {
                'number': number,
            },
        }

    def test_simple_call(self):
        """
        Test a simple call with two participants.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ended - A and B hang up (reason: completed)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress = self.generate_in_progress_json(call_id, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ended = self.generate_ended_json(call_id, caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.

    def test_no_pickup(self):
        """
        Test a call where the phone rings, but is not answered.

        Notifications:
            ringing - A calls B
            ended - A and B hang up (reason: busy or no-answer, differs per device)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        ended = self.generate_ended_json(call_id, reason='busy', caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(crs[0].destination, None)  # There still shouldn't be a destination.

    def test_automatic_pickup(self):
        """
        Test a call where the phone doesn't ring, because it's automatically answered.

        Notifications:
            in_progress - A calls B, B automatically picks up
            ended - A and B hang up (reason: busy or no-answer, differs per device)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)

        in_progress = self.generate_in_progress_json(call_id, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # Caller should be filled.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled.

        ended = self.generate_ended_json(call_id, reason='busy', caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.

    def test_unavailable(self):
        """
        Test a call where the called person is unavailable (phone off or do not disturb), phone doesn't ring.

        Notifications:
            ended - A calls B (reason: busy)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)

        ended = self.generate_ended_json(call_id, reason='busy', caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # There shouldn't be a destination.

    def test_warm_transfer(self):
        """
        Test a call where B transfers the call to C, after talking to C.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ringing - B calls C
            in-progress - B calls with C
            warm-transfer - B connects A and C
            ended - A and C hang up (reason: completed)
        """
        call_id_ab = '100'
        call_id_bc = '101'

        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        participant_b_internal = deepcopy(participant_b)
        participant_b_internal['number'] = str(participant_b['account_number'])
        participant_c = self.generate_participant(internal=True)

        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        destination_c = self.generate_destination(number=participant_c['number'], targets=[participant_c, ])

        ringing_ab = self.generate_ringing_json(call_id_ab, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress_ab = self.generate_in_progress_json(call_id_ab, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ringing_bc = self.generate_ringing_json(call_id_bc, caller=participant_b_internal, destination=destination_c)
        request = self.user.post(reverse(self.list_url), ringing_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        in_progress_bc = self.generate_in_progress_json(
            call_id_bc, caller=participant_b_internal, target=participant_c
        )
        request = self.user.post(reverse(self.list_url), in_progress_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        warm_transfer = self.generate_warm_transfer_json(
            call_id_ab, call_id_bc, caller=participant_a, target=participant_c, redirector=participant_b_internal
        )
        request = self.user.post(reverse(self.list_url), warm_transfer)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(len(transfers), 1)  # There should be one call transfer.
        self.assertEqual(transfers[0].destination.number, participant_c['number'])

        ended = self.generate_ended_json(call_id_ab, caller=participant_a, number=participant_c['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(len(crs[0].transfers.all()), 1)  # There should be one call transfer.

    def test_cold_transfer(self):
        """
        Test a call where B transfers the call to C, without talking to C.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ringing - B calls C
            cold-transfer - B connects A and C
            in-progress - A calls with C
            ended - A and C hang up (reason: completed)
        """
        call_id_ab = '100'
        call_id_bc = '101'

        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        participant_b_internal = deepcopy(participant_b)
        participant_b_internal['number'] = str(participant_b['account_number'])
        participant_c = self.generate_participant(internal=True)

        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        destination_c = self.generate_destination(number=participant_c['number'], targets=[participant_c, ])

        ringing_ab = self.generate_ringing_json(call_id_ab, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress_ab = self.generate_in_progress_json(call_id_ab, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ringing_bc = self.generate_ringing_json(call_id_bc, caller=participant_b_internal, destination=destination_c)
        request = self.user.post(reverse(self.list_url), ringing_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        cold_transfer = self.generate_cold_transfer_json(
            call_id_ab, call_id_bc, caller=participant_a, destination=destination_c, redirector=participant_b_internal
        )
        request = self.user.post(reverse(self.list_url), cold_transfer)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(len(transfers), 1)  # There should be one call transfer.
        self.assertEqual(transfers[0].destination, None)  # With cold transfers there is no destination yet.

        in_progress_ac = self.generate_in_progress_json(call_id_ab, caller=participant_a, target=participant_c)
        request = self.user.post(reverse(self.list_url), in_progress_ac)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(transfers[0].destination.number, participant_c['number'])

        ended = self.generate_ended_json(call_id_ab, caller=participant_a, number=participant_c['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(len(crs[0].transfers.all()), 1)  # There should be one call transfer.

    def test_call_pickup(self):
        """
        Test a call where two phones (B & C) are in the same pickup group, B is called, C picks up.

        Notifications:
            ringing - A calls B
            in-progress - A calls with C
            ended - A and C hang up (reden: completed)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        participant_c = self.generate_participant(internal=True)

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress = self.generate_in_progress_json(call_id, caller=participant_a, target=participant_c)
        request = self.user.post(reverse(self.list_url), in_progress)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_c['number'])  # Destination should be filled now.

        ended = self.generate_ended_json(call_id, caller=participant_a, number=participant_c['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.

    def test_callgroup(self):
        """
        Test a call where A calls to B and B is a callgroup with multiple participants.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ended - A and B hang up (reason: completed)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        destination_number = participant_b['number']
        participant_list = [
            participant_b,
            self.generate_participant(number=destination_number, internal=True),
            self.generate_participant(number=destination_number, internal=True),
            self.generate_participant(number=destination_number, internal=True),
            self.generate_participant(number=destination_number, internal=True),
        ]
        destination = self.generate_destination(number=destination_number, targets=participant_list)

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress = self.generate_in_progress_json(call_id, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ended = self.generate_ended_json(call_id, caller=participant_a, number=destination_number)
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.

    def test_internal_caller(self):
        """
        Test a simple call with two participants, where the caller is an internal number (between colleagues).

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ended - A and B hang up (reason: completed)
        """
        call_id = '100'
        number_a = self.generate_number(internal=True)
        participant_a = self.generate_participant(number=number_a, internal=True)
        number_b = self.generate_number(internal=True)
        participant_b = self.generate_participant(number=number_b, internal=True)
        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 0)  # There should not be a call record in the database.

        in_progress = self.generate_in_progress_json(call_id, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 0)  # There should not be a call record in the database.

        ended = self.generate_ended_json(call_id, caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 0)  # There should not be a call record in the database.

    def test_fixed_destination(self):
        """
        Test a simple call with two participants, which is routed to a fixed destination.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ended - A and B hang up (reason: completed)
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant()
        # The exception for fixed destination is that everything seems external but there is a user_number.
        participant_b['user_numbers'] = [str(randrange(100, 999)), ]
        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress = self.generate_in_progress_json(call_id, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ended = self.generate_ended_json(call_id, caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.

    def test_call_forwarding(self):
        """
        Test a call where the user has set their phone to automatically forward phone calls to a different number.

        Notificaitons:
            ringing - A calls B
            ringing - A calls B & C
            in-progress or ended, depends if someone answers the call.
        """
        call_id = '100'
        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        participant_c = self.generate_participant(internal=True)
        destination_bc = self.generate_destination(number=participant_b['number'], targets=[
            participant_b, participant_c,
        ])

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        ringing = self.generate_ringing_json(call_id, caller=participant_a, destination=destination_bc)
        request = self.user.post(reverse(self.list_url), ringing)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        ended = self.generate_ended_json(call_id, caller=participant_a, number=participant_b['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.

    def test_warm_transfer_with_switched_ids(self):
        """
        Test a call where B transfers the call to C, after talking to C and the call and merged ids are switched.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ringing - B calls C
            in-progress - B calls with C
            warm-transfer - B connects A and C (switch call_id and merged_id)
            ended - A and C hang up (reason: completed)
        """
        call_id_ab = '100'
        call_id_bc = '101'

        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        participant_b_internal = deepcopy(participant_b)
        participant_b_internal['number'] = str(participant_b['account_number'])
        participant_c = self.generate_participant(internal=True)

        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        destination_c = self.generate_destination(number=participant_c['number'], targets=[participant_c, ])

        ringing_ab = self.generate_ringing_json(call_id_ab, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress_ab = self.generate_in_progress_json(call_id_ab, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ringing_bc = self.generate_ringing_json(call_id_bc, caller=participant_b_internal, destination=destination_c)
        request = self.user.post(reverse(self.list_url), ringing_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        in_progress_bc = self.generate_in_progress_json(
            call_id_bc, caller=participant_b_internal, target=participant_c
        )
        request = self.user.post(reverse(self.list_url), in_progress_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        warm_transfer = self.generate_warm_transfer_json(
            call_id_bc, call_id_ab, caller=participant_a, target=participant_c, redirector=participant_b_internal
        )
        request = self.user.post(reverse(self.list_url), warm_transfer)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(len(transfers), 1)  # There should be one call transfer.
        self.assertEqual(transfers[0].destination.number, participant_c['number'])

        ended = self.generate_ended_json(call_id_bc, caller=participant_a, number=participant_c['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(len(crs[0].transfers.all()), 1)  # There should be one call transfer.

    def test_cold_transfer_with_switched_ids(self):
        """
        Test a call where B transfers the call to C, without talking to C and the call and merged ids are switched.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ringing - B calls C
            cold-transfer - B connects A and C (switch call_id and merged_id)
            in-progress - A calls with C
            ended - A and C hang up (reason: completed)
        """
        call_id_ab = '100'
        call_id_bc = '101'

        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        participant_b_internal = deepcopy(participant_b)
        participant_b_internal['number'] = str(participant_b['account_number'])
        participant_c = self.generate_participant(internal=True)

        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        destination_c = self.generate_destination(number=participant_c['number'], targets=[participant_c, ])

        ringing_ab = self.generate_ringing_json(call_id_ab, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress_ab = self.generate_in_progress_json(call_id_ab, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ringing_bc = self.generate_ringing_json(call_id_bc, caller=participant_b_internal, destination=destination_c)
        request = self.user.post(reverse(self.list_url), ringing_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        cold_transfer = self.generate_cold_transfer_json(
            call_id_bc, call_id_ab, caller=participant_a, destination=destination_c, redirector=participant_b_internal
        )
        request = self.user.post(reverse(self.list_url), cold_transfer)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(len(transfers), 1)  # There should be one call transfer.
        self.assertEqual(transfers[0].destination, None)  # With cold transfers there is no destination yet.

        in_progress_ac = self.generate_in_progress_json(call_id_bc, caller=participant_a, target=participant_c)
        request = self.user.post(reverse(self.list_url), in_progress_ac)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(transfers[0].destination.number, participant_c['number'])

        ended = self.generate_ended_json(call_id_bc, caller=participant_a, number=participant_c['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(len(crs[0].transfers.all()), 1)  # There should be one call transfer.

    def test_cold_transfer_without_answer(self):
        """
        Test a call where B transfers the call to C, without talking to C and where C doesn't answer.

        Notifications:
            ringing - A calls B
            in-progress - A calls with B
            ringing - B calls C
            cold-transfer - B connects A and C
            ended - A and C hang up (reason: completed)
        """
        call_id_ab = '100'
        call_id_bc = '101'

        participant_a = self.generate_participant()
        participant_b = self.generate_participant(internal=True)
        participant_b_internal = deepcopy(participant_b)
        participant_b_internal['number'] = str(participant_b['account_number'])
        participant_c = self.generate_participant(internal=True)

        destination_b = self.generate_destination(number=participant_b['number'], targets=[participant_b, ])
        destination_c = self.generate_destination(number=participant_c['number'], targets=[participant_c, ])

        ringing_ab = self.generate_ringing_json(call_id_ab, caller=participant_a, destination=destination_b)
        request = self.user.post(reverse(self.list_url), ringing_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.RINGING)  # The status should be ringing.
        self.assertEqual(crs[0].caller.number, participant_a['number'])  # There should be a caller saved.
        self.assertEqual(crs[0].destination, None)  # Don't save the destination yet.

        in_progress_ab = self.generate_in_progress_json(call_id_ab, caller=participant_a, target=participant_b)
        request = self.user.post(reverse(self.list_url), in_progress_ab)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.IN_PROGRESS)  # The status should be in progress.
        self.assertEqual(crs[0].destination.number, participant_b['number'])  # Destination should be filled now.

        ringing_bc = self.generate_ringing_json(call_id_bc, caller=participant_b_internal, destination=destination_c)
        request = self.user.post(reverse(self.list_url), ringing_bc)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should still only be one call record.

        cold_transfer = self.generate_cold_transfer_json(
            call_id_ab, call_id_bc, caller=participant_a, destination=destination_c, redirector=participant_b_internal
        )
        request = self.user.post(reverse(self.list_url), cold_transfer)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        transfers = crs[0].transfers.all()
        self.assertEqual(len(transfers), 1)  # There should be one call transfer.
        self.assertEqual(transfers[0].destination, None)  # With cold transfers there is no destination yet.

        ended = self.generate_ended_json(call_id_ab, caller=participant_a, number=participant_c['number'])
        request = self.user.post(reverse(self.list_url), ended)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        crs = CallRecord.objects.all()
        self.assertEqual(len(crs), 1)  # There should only be one call record.
        self.assertEqual(crs[0].status, CallRecord.ENDED)  # The status should be ended.
        self.assertEqual(len(crs[0].transfers.all()), 0)  # There should be no call transfers.

from unittest import SkipTest

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from lily.calls.models import CallRecord, CallTransfer
from lily.tests.utils import UserBasedTest


class CallNotificationsAPITestCase(UserBasedTest, APITestCase):
    list_url = 'callnotification-list'
    detail_url = 'callnotification-detail'

    def test_simple_call(self):
        """
        Test a simple call with two participants.
        """
        # ringing - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.159",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # in-progress - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.159",
            "timestamp": "2017-07-20T13:18:39+00:00",
            "status": "in-progress",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - A calls B (reason: completed).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.159",
            "timestamp": "2017-07-20T13:19:39+00:00",
            "status": "ended",
            "reason": "completed",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record.
        self.assertEqual(len(CallRecord.objects.all()), 1)

    def test_no_pickup(self):
        """
        Test a call where the phone rings, but is not answered.
        """
        # ringing - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.160",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - A calls B (reason: busy or no-answer dependent on the type of phone).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.160",
            "timestamp": "2017-07-20T13:18:39+00:00",
            "status": "ended",
            "reason": "busy",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record.
        self.assertEqual(len(CallRecord.objects.all()), 1)

        # TODO: also test reason:no-answer, because the reason is phone dependent.

    def test_unavailable(self):
        """
        Test a call where the called person in unavailable (phone off or do not disturb), phone doesn't ring.
        """
        # ended - A calls B (reason: busy).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.161",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ended",
            "reason": "busy",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record.
        self.assertEqual(len(CallRecord.objects.all()), 1)

    def test_attended_transfer(self):
        """
        Test a call with an attended transfer:
            A calls B.
            B wants to transfer to C.
            B calls C and they have a conversation.
            B actually transfers A to C.
        """
        # ringing - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.162",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # in-progress - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.162",
            "timestamp": "2017-07-20T13:18:39+00:00",
            "status": "in-progress",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ringing - B calls C.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.163",
            "timestamp": "2017-07-20T13:19:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        # TODO: assert that this second call is not saved because it is between two internal numbers.

        # in-progress - B calls C.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.163",
            "timestamp": "2017-07-20T13:20:39+00:00",
            "status": "in-progress",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        # TODO: assert that this second call is not saved because it is between two internal numbers.

        # transfer - B connects A and C.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.162",
            "merged_id": "24c562241e9f-1502719948.163",
            "timestamp": "2017-07-20T13:21:39+00:00",
            "status": "transfer",
            "version": "v1",
            "direction": "inbound",
            "party1": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "party2": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            },
            "redirector": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # TODO: check the transfer object is created correctly.

        # ended - B and C hang up (reason: transferred).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.163",
            "timestamp": "2017-07-20T13:22:39+00:00",
            "status": "ended",
            "reason": "transfered",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - A and C hang up (reason: completed).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.162",
            "timestamp": "2017-07-20T13:23:39+00:00",
            "status": "ended",
            "reason": "completed",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record and one transfer record.
        self.assertEqual(len(CallRecord.objects.all()), 1)
        self.assertEqual(len(CallTransfer.objects.all()), 1)

    def test_blind_transfer(self):
        """
        Test a call with a blind transfer:
            A calls B.
            B wants to transfer to C.
            B immediately transfers A to C without checking in with C first.
        """
        # ringing - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.164",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # in-progress - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.164",
            "timestamp": "2017-07-20T13:18:39+00:00",
            "status": "in-progress",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ringing - B calls C.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.165",
            "timestamp": "2017-07-20T13:19:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # transfer - B connects A and C.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.164",
            "merged_id": "24c562241e9f-1502719948.165",
            "timestamp": "2017-07-20T13:20:39+00:00",
            "status": "transfer",
            "version": "v1",
            "direction": "inbound",
            "party1": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "party2": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            },
            "redirector": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - B and C hang up (reason: transferred).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.165",
            "timestamp": "2017-07-20T13:21:39+00:00",
            "status": "ended",
            "reason": "transfered",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # in-progress - A calls C
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.164",
            "timestamp": "2017-07-20T13:22:39+00:00",
            "status": "in-progress",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - A and C hang up (reason: completed).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.164",
            "timestamp": "2017-07-20T13:23:39+00:00",
            "status": "ended",
            "reason": "transfered",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record and one transfer record.
        self.assertEqual(len(CallRecord.objects.all()), 1)
        self.assertEqual(len(CallTransfer.objects.all()), 1)

    def test_semi_attended_transfer(self):
        """
        Test a call with a semi attended transfer:
            A calls B.
            B wants to transfer to C.
            B calls C but doesn't wait for C to pick up the phone.
            B transfers A to C before C picked up the phone.
        """
        # ringing - A calls B.
        # in-progress - A calls B.
        # ringing - B calls C.
        # transfer - B connects A and C.
        # ended - B and C hang up (reason: transferred).
        # in-progress - A calls C.
        # ended - A and C hang up (reason: completed).

        # This is exactly the same as blind transfer.
        raise SkipTest()

    def test_call_pickup(self):
        """
        Test a call with a call-pickup:
            A calls B.
            C is in the same pickup group as B.
            C picks up the call that was meant for B.
        """
        # ringing - A calls B.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.166",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # transfer - B connects A and C.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.166",
            "merged_id": "24c562241e9f-1502719948.165",
            "timestamp": "2017-07-20T13:18:39+00:00",
            "status": "transfer",
            "version": "v1",
            "direction": "inbound",
            "party1": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "party2": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            },
            "redirector": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - A and C hang up (reason: completed).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.166",
            "timestamp": "2017-07-20T13:19:39+00:00",
            "status": "ended",
            "reason": "completed",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record and one transfer record.
        self.assertEqual(len(CallRecord.objects.all()), 1)
        self.assertEqual(len(CallTransfer.objects.all()), 1)

    def test_callgroup(self):
        """
        Test a call with a callgroup:
            A calls callgroup (multiple phones ring).
            Someone picks up in the callgroup (B).
            The conversation ends.
        """
        # ringing - A calls callgroup.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.167",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 234,
                "number": "+315080090000",
                "user_numbers": ["678"],
                "name": "Luuk"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.167",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 235,
                "number": "+315080090000",
                "user_numbers": ["679"],
                "name": "Sjoerd"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.167",
            "timestamp": "2017-07-20T13:17:39+00:00",
            "status": "ringing",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 236,
                "number": "+315080090000",
                "user_numbers": ["680"],
                "name": "Tom"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # in-progress - Someone picks up in the callgroup.
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.167",
            "timestamp": "2017-07-20T13:18:39+00:00",
            "status": "in-progress",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 236,
                "number": "+315080090000",
                "user_numbers": ["680"],
                "name": "Tom"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # ended - A and B hang up (reason: completed).
        request = self.user.post(reverse(self.list_url), {
            "call_id": "24c562241e9f-1502721212.167",
            "timestamp": "2017-07-20T13:19:39+00:00",
            "status": "ended",
            "reason": "completed",
            "version": "v1",
            "direction": "inbound",
            "caller": {
                "account_number": None,
                "number": "+31508009044",
                "user_numbers": [],
                "name": "Allard"
            },
            "destination": {
                "account_number": 236,
                "number": "+315080090000",
                "user_numbers": ["680"],
                "name": "Tom"
            }
        })
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        # There should only be one call record.
        self.assertEqual(len(CallRecord.objects.all()), 1)

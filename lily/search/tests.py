import json
from datetime import datetime, timedelta

from django.urls import reverse
from pytz import utc
from rest_framework import status
from rest_framework.test import APITestCase

from lily.accounts.factories import AccountFactory
from lily.cases.factories import CaseFactory, CaseStatusFactory
from lily.cases.models import Case
from lily.contacts.factories import ContactFactory
from lily.contacts.models import Function
from lily.deals.factories import DealFactory, DealStatusFactory
from lily.deals.models import Deal
from lily.notes.factories import NoteFactory
from lily.notes.models import Note
from lily.tests.utils import UserBasedTest
from lily.users.factories import LilyUserFactory
from lily.utils.models.factories import PhoneNumberFactory


class InternalNumberSearchAPITestCase(UserBasedTest, APITestCase):
    search_url = 'search_internal_number_view'

    @classmethod
    def setUpTestData(cls):
        super(InternalNumberSearchAPITestCase, cls).setUpTestData()

        cls.four_days_ago = datetime.now(tz=utc) - timedelta(days=4)
        cls.five_days_ago = datetime.now(tz=utc) - timedelta(days=5)
        cls.nine_days_ago = datetime.now(tz=utc) - timedelta(days=9)

        cls.case_status_new = CaseStatusFactory.create(tenant=cls.user_obj.tenant, name='New')
        cls.case_status_closed = CaseStatusFactory.create(tenant=cls.user_obj.tenant, name='Closed')
        cls.deal_status_open = DealStatusFactory.create(tenant=cls.user_obj.tenant, name='Open')
        cls.deal_status_lost = DealStatusFactory.create(tenant=cls.user_obj.tenant, name='Lost')

        cls.phone_number = PhoneNumberFactory(tenant=cls.user_obj.tenant, number='+31611223344')
        cls.contact = ContactFactory.create(tenant=cls.user_obj.tenant)
        cls.contact.phone_numbers.add(cls.phone_number)

    def test_contact_open_deal_open_case_notes(self):
        """
        Test having a contact with open deals and cases. Both with notes.
        """
        # There are open cases and open deals, both have attached notes. The most recent note is for a case.
        cases = CaseFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Case.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))

        case = cases[0]
        case.contact = self.contact
        case.is_deleted = False
        case.status = self.case_status_new
        case.modified = datetime(2018, 1, 3, tzinfo=utc)
        case.update_modified = False
        case.save()

        case_notes = NoteFactory.create_batch(
            size=5,
            tenant=self.user_obj.tenant,
            gfk_content_type=case.content_type,
            gfk_object_id=case.id
        )

        for note in case_notes:
            case.notes.add(note)

        case_note = case_notes[0]

        deals = DealFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Deal.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))

        deal = deals[0]
        deal.is_deleted = False
        deal.status = self.deal_status_open
        deal.contact = self.contact
        deal.modified = datetime(2018, 1, 2, tzinfo=utc)
        deal.update_modified = False
        deal.save()

        deal_notes = NoteFactory.create_batch(
            size=5,
            tenant=self.user_obj.tenant,
            gfk_content_type=deal.content_type,
            gfk_object_id=deal.id
        )

        for note in deal_notes:
            deal.notes.add(note)

        deal_note = deal_notes[0]

        Note.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))
        Note.objects.filter(pk=case_note.pk).update(modified=datetime(2018, 2, 3, tzinfo=utc))
        Note.objects.filter(pk=deal_note.pk).update(modified=datetime(2018, 2, 2, tzinfo=utc))

        assigned_to_user = case.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

        # There are open cases and open deals, both have attached notes. The most recent note is for a deal.
        Note.objects.filter(pk=case_note.pk).update(modified=datetime(2018, 2, 2, tzinfo=utc))
        Note.objects.filter(pk=deal_note.pk).update(modified=datetime(2018, 2, 3, tzinfo=utc))

        assigned_to_user = deal.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_open_deal_open_case_no_notes(self):
        """
        Test having a contact with open deals and cases. Both without notes.
        """
        # There are open cases and open deals, both have no attached notes. The case is the most recent edited.
        cases = CaseFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Case.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))

        case = cases[0]
        case.contact = self.contact
        case.is_deleted = False
        case.status = self.case_status_new
        case.modified = datetime(2018, 1, 3, tzinfo=utc)
        case.update_modified = False
        case.save()

        assigned_to_user = case.assigned_to

        deals = DealFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Deal.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))

        deal = deals[0]
        deal.is_deleted = False
        deal.status = self.deal_status_open
        deal.contact = self.contact
        deal.modified = datetime(2018, 1, 2, tzinfo=utc)
        deal.update_modified = False
        deal.save()

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

        # There are open cases and open deals, both have no attached notes. The deal is the most recent edited.
        Case.objects.filter(pk=case.pk).update(modified=datetime(2018, 3, 2, tzinfo=utc))
        Deal.objects.filter(pk=deal.pk).update(modified=datetime(2018, 3, 3, tzinfo=utc))

        assigned_to_user = deal.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_open_case(self):
        """
        Test having a contact with only open cases.
        """
        cases = CaseFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Case.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))

        case = cases[0]
        case.contact = self.contact
        case.is_deleted = False
        case.status = self.case_status_new
        case.modified = datetime(2018, 1, 3, tzinfo=utc)
        case.update_modified = False
        case.save()

        assigned_to_user = case.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_open_deal(self):
        """
        Test having a contact with only open deals.
        """
        deals = DealFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Deal.objects.all().update(modified=datetime(2018, 1, 1, tzinfo=utc))

        deal = deals[0]
        deal.is_deleted = False
        deal.status = self.deal_status_open
        deal.contact = self.contact
        deal.modified = datetime(2018, 1, 2, tzinfo=utc)
        deal.update_modified = False
        deal.save()

        assigned_to_user = deal.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_closed_deal_closed_case(self):
        """
        Test having a contact with no open deals or cases. There are both a case and deal closed less then a week ago.
        """
        # The case closed the most recent.
        cases = CaseFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Case.objects.all().update(
            modified=datetime(2018, 1, 1, tzinfo=utc),
            status=self.case_status_closed
        )

        case = cases[0]
        case.contact = self.contact
        case.is_deleted = False
        case.status = self.case_status_closed
        case.modified = self.four_days_ago
        case.update_modified = False
        case.save()

        deals = DealFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Deal.objects.all().update(
            modified=datetime(2018, 1, 1, tzinfo=utc),
            status=self.deal_status_lost
        )

        deal = deals[0]
        deal.is_deleted = False
        deal.status = self.deal_status_lost
        deal.contact = self.contact
        deal.modified = self.five_days_ago
        deal.update_modified = False
        deal.save()

        assigned_to_user = case.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

        # The deal closed the most recent.
        case.modified = self.five_days_ago
        case.update_modified = False
        case.save()

        deal.modified = self.four_days_ago
        deal.update_modified = False
        deal.save()

        assigned_to_user = deal.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_closed_case(self):
        """
        Test having a contact with no open deals or cases. There is only a case closed less than a week ago.
        """
        cases = CaseFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Case.objects.all().update(
            modified=datetime(2018, 1, 1, tzinfo=utc),
            status=self.case_status_closed
        )

        DealFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Deal.objects.all().update(
            modified=datetime(2018, 1, 1, tzinfo=utc),
            status=self.deal_status_lost
        )

        case = cases[0]
        case.contact = self.contact
        case.is_deleted = False
        case.status = self.case_status_closed
        case.modified = self.four_days_ago
        case.update_modified = False
        case.save()

        assigned_to_user = case.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_closed_deal(self):
        """
        Test having a contact with no open deals or cases. There is only a deal closed less than a week ago.
        """
        CaseFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Case.objects.all().update(
            modified=datetime(2018, 1, 1, tzinfo=utc),
            status=self.case_status_closed
        )

        deals = DealFactory.create_batch(size=5, tenant=self.user_obj.tenant)
        Deal.objects.all().update(
            modified=datetime(2018, 1, 1, tzinfo=utc),
            status=self.deal_status_lost
        )

        deal = deals[0]
        deal.is_deleted = False
        deal.status = self.deal_status_lost
        deal.contact = self.contact
        deal.modified = self.five_days_ago
        deal.update_modified = False
        deal.save()

        assigned_to_user = deal.assigned_to

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def test_contact_closed_deals_cases_account(self):
        """
        Test having a contact attached to a contact with no cases or deals.
        """
        assigned_to_user = LilyUserFactory.create(tenant=self.user_obj.tenant, is_active=True)
        account = AccountFactory.create(tenant=self.user_obj.tenant, assigned_to=assigned_to_user)
        Function.objects.create(account=account, contact=self.contact)

        # Make api call.
        response = self.user.get(reverse(self.search_url, kwargs={'number': self.phone_number.number}))

        # Verify response.
        self._verify_response(response, assigned_to_user)

    def _verify_response(self, response, user):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(content.get('internal_number'), user.internal_number)
        self.assertEqual(content.get('user'), user.id)

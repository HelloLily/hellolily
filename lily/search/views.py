from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.response import HttpResponse
from django.views.generic.base import View

import anyjson

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.utils.functions import parse_phone_number
from lily.search.functions import search_number


class PhoneNumberSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        number = kwargs.get('number', None)

        if number:
            # For now we'll always convert the phone number to a certain format.
            # In the future we might change how we handle phone numbers.
            number = parse_phone_number(number)

        response = {
            'data': {
                'accounts': [],
                'contacts': [],
            },
        }

        # TODO LILY-2786: Optimize number fetching queries.
        # This function gets all accounts and contacts from the db, only
        # returns the first one and then only gets the PK of the object here.
        # These queries can be much faster and more simple.
        results = search_number(self.request.user.tenant_id, number)

        # Return only the primary keys of the accounts and contacts
        for account in results['data']['accounts']:
            response['data']['accounts'].append(account.id)

        for contact in results['data']['contacts']:
            response['data']['contacts'].append(contact.id)

        return HttpResponse(anyjson.dumps(response), content_type='application/json; charset=utf-8')


class InternalNumberSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # TODO LILY-2785: These queries should be optimized and tested.
        number = kwargs.get('number', None)

        if number:
            # For now we'll always convert the phone number to a certain format.
            # In the future we might change how we handle phone numbers.
            number = parse_phone_number(number)

        results = self._search_number(number)

        response_format = request.GET.get('format')

        if response_format and response_format.lower() == 'grid':
            name = ''
            internal_number = results.get('internal_number', '')

            result = search_number(request.user.tenant_id, number, False)
            data = result.get('data')
            accounts = data.get('accounts')
            contacts = data.get('contacts')

            if contacts:
                name = contacts[0].full_name
            elif accounts:
                name = accounts[0].name

            if name:
                response = 'status=ACK&callername=%s' % name

                if internal_number:
                    response += '&destination=%s' % internal_number
            else:
                response = 'status=NAK'

            return HttpResponse(response, content_type='text/plain; charset=utf-8')
        else:
            user = results.get('user')

            if user:
                results['user'] = user.id

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

    def _get_last_contacted(self, number):
        """
        Look for an account with the given number.
        If it exists look for a case or deal with a contact and return
        the contact and assignee of the case or deal.

        Args:
            number (str): Contains the number we want to look for.
        Returns:
            contact (obj): Contact belonging to the case/deal.
            assignee (obj): Assignee of the case/deal.
        """
        # TODO LILY-2785: These queries should be optimized and tested.
        account = Account.objects.filter(phone_numbers__number=number).order_by('-modified').first()

        contact = None
        assignee = None

        if account:
            # Look for cases/deal which have a contact.
            case = Case.objects.filter(account=account, contact__isnull=False).order_by('-modified').first()

            if case:
                contact = case.contact
                assignee = case.assigned_to
            else:
                deal = Deal.objects.filter(account=account, contact__isnull=False).order_by('-modified').first()

                if deal:
                    contact = deal.contact
                    assignee = deal.assigned_to

        return contact, assignee

    def _search_number(self, number):
        """
        Looks for a contact based on the given number and returns the internal number of the user assigned to a deal,
        case or account based on that contact.

        Args:
            number (str): Contains the number we want to look for.

        Returns:
            internal_number (int): The internal number of the user.
            user (int): ID of the user the internal number belongs to.
        """
        # TODO LILY-2785: These queries should be optimized and tested.
        # Try to find a contact with the given phone number.
        contact = Contact.elastic_objects.filter(phone_numbers__number=number).order_by('-modified').first()

        if contact:
            user = None
        else:
            contact, user = self._get_last_contacted(number)

        week_ago = date.today() - timedelta(days=7)

        if contact:
            cases = Case.objects.filter(contact=contact, is_deleted=False).order_by('-modified')
            open_case = cases.filter(status__name='New').first()

            deals = Deal.objects.filter(
                contact=contact,
                status__name='Open',
                is_deleted=False
            ).order_by('-modified')
            open_deal = deals.filter(status__name='Open').first()

            if open_case and open_deal:
                latest_case_note = open_case.notes.all().order_by('-modified').first()
                latest_deal_note = open_deal.notes.all().order_by('-modified').first()

                # If there is an open deal and an open case the one with the most recent note.
                if latest_case_note and latest_deal_note:
                    # Check the latest modified note.
                    if latest_case_note.modified > latest_deal_note.modified:
                        user = open_case.assigned_to
                    else:
                        user = open_deal.assigned_to
                else:
                    # No notes for both types, so check modified date.
                    if open_case.modified > open_deal.modified:
                        user = open_case.assigned_to
                    else:
                        user = open_deal.assigned_to
            elif open_case:
                # No open deal, so use open case.
                user = open_case.assigned_to
            elif open_deal:
                # No open case, so use open deal.
                user = open_deal.assigned_to
            else:
                # Get closed cases and deals.
                latest_closed_case = cases.filter(Q(created__gte=week_ago) & Q(status__name='Closed')).first()
                latest_closed_deal = deals.filter(Q(created__lte=week_ago) &
                                                  (Q(status__name='Won') | Q(status__name='Lost'))).first()

                if latest_closed_case and latest_closed_deal:
                    if latest_closed_case.modified > latest_closed_deal.modified:
                        user = latest_closed_case.assigned_to
                    else:
                        user = latest_closed_deal.assigned_to
                elif latest_closed_case:
                    # No closed deal, so use closed case.
                    user = latest_closed_case.assigned_to
                elif latest_closed_deal:
                    # No closed case, so use closed deal.
                    user = latest_closed_deal.assigned_to
                else:
                    if contact.accounts.count():
                        user = contact.accounts[0].assigned_to
        else:
            # Try to find an account with the given phone number.
            account = Account.objects.filter(phone_numbers__number=number).first()

            if account:
                user = account.assigned_to

        if user:
            return {
                'internal_number': user.internal_number,
                'user': user,
            }

        return {}

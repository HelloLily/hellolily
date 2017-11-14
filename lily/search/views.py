from datetime import date, timedelta, datetime

import anyjson
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.response import HttpResponse
from django.views.generic.base import View

from pytz import utc
from lily.accounts.models import Account

from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.search.functions import search_number
from lily.utils.models.models import PhoneNumber
from lily.utils.functions import parse_phone_number


class PhoneNumberSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        number = kwargs.get('number', None)

        response = {
            'data': {
            },
        }

        # TODO LILY-2786: Optimize number fetching queries.
        account, contact = search_number(self.request.user.tenant_id, number)
        # This function gets all accounts and contacts from the db, only
        # returns the first one and then only gets the PK of the object here.
        # These queries can be much faster and more simple.

        if account:
            response['data']['account'] = {'id': account.id, 'name': account.name}

        if contact:
            response['data']['contact'] = {'id': contact.id, 'name': contact.full_name}

        return HttpResponse(anyjson.dumps(response), content_type='application/json; charset=utf-8')


class InternalNumberSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        phone_number = kwargs.get('number', None)
        # TODO LILY-2785: These queries should be optimized and tested.

        if phone_number:
            # For now we'll always convert the phone number to a certain format.
            # In the future we might change how we handle phone numbers.
            phone_number = parse_phone_number(phone_number)

        results = self._get_user_internal_number(phone_number)

        response_format = request.GET.get('format')
        if response_format and response_format.lower() == 'grid':
            name = None
            internal_number = results.get('internal_number', '')

            account, contact = search_number(request.user.tenant_id, phone_number)

            if contact:
                name = contact.full_name
            elif account:
                name = account.name

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

    def _get_contact_assignee_by_account(self, account):
        """
        Return a contact and assignee of a case or deal belonging to the provided account.

        Args:
            account (obj): Account to which cases or deals belong to.

        Returns:
            contact (obj): Contact belonging to the case or deal.
            assignee (obj): Assignee of the case or deal.
        """
        tenant = self.request.user.tenant
        account = Account.objects.filter(phone_numbers__number=number).order_by('-modified').first()

        contact = None
        assignee = None

        if account:
            # Look for case and deal with a contact.
            case = Case.objects.filter(
                tenant=tenant,
                account=account,
                contact__isnull=False,
                is_deleted=False
            ).order_by(
                '-modified'
            ).first()
            ).order_by(
                '-modified'
            ).first()

                if deal:
                    contact = deal.contact
                    assignee = deal.assigned_to
            elif deal:
                contact = deal.contact
                assignee = deal.assigned_to

        return contact, assignee

    def _get_user_internal_number(self, phone_number):
        """
        First look up a contact or account by the provided phone number. Next determine for that contact or account
        the case / deal with the latest interaction. Return that user and its internal number to which that deal or
        case is assigned to.

        Args:
            phone_number (str): Formatted phone number.

        Returns:
            JSON string containing:
                internal_number (int): The internal number of the user.
                user (int): ID of the user the internal number belongs to.
        """
        tenant = self.request.user.tenant
        contact = Contact.elastic_objects.filter(phone_numbers__number=number).order_by('-modified').first()
        user = None

        if hits:
            contact = hits[0]
            number=phone_number
        )

        # Try to find a contact with the given phone number.
        contact = Contact.objects.filter(
            tenant=tenant,
            phone_numbers__in=phone_numbers,
        ).order_by(
            '-modified'
        ).first()

        # Try to find an account with the given phone number.
        account = Account.objects.filter(
            tenant=tenant,
            phone_numbers__in=phone_numbers,
        ).order_by(
            '-modified'
        ).first()
        if not contact:
            contact, assignee = self._get_contact_assignee_by_account(account)

        if contact:
            cases = Case.objects.filter(
                contact=contact,
                is_deleted=False
            ).order_by('-modified')
            open_case = cases.filter(status__name='New').first()

            deals = Deal.objects.filter(
                contact=contact,
                is_deleted=False
            ).order_by('-modified')
            open_deal = deals.filter(status__name='Open').first()

            if open_case and open_deal:
                latest_case_note = open_case.notes.all().order_by('-modified').first()
                latest_deal_note = open_deal.notes.all().order_by('-modified').first()

                # If there is an open deal and an open case the one with the most recent note.
                if latest_case_note and latest_deal_note:
                    # Get the user of the case or deal with the note with the most recent interaction.
                    if latest_case_note.modified > latest_deal_note.modified:
                        user = open_case.assigned_to
                    else:
                        user = open_deal.assigned_to
                else:
                    # No attached notes for both the case or deal.
                    # Get the user of the case or deal with the most recent interaction.
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
                week_ago = date.today() - timedelta(days=7)
                week_ago = datetime(week_ago.year, week_ago.month, week_ago.day, tzinfo=utc)

                # Get a case that is not older then a week and closed.
                latest_closed_case = cases.filter(
                    Q(created__gte=week_ago) &
                    Q(status__name='Closed')
                ).first()
                # Get a deal that is not older then a week and won or lost.
                latest_closed_deal = deals.filter(
                    Q(created__gte=week_ago) &
                    (Q(status__name='Won') | Q(status__name='Lost'))
                ).first()

                if latest_closed_case and latest_closed_deal:
                    # Get the user of the case or deal with the most recent interaction.
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
                    # None of the above rules applies, so use account if possible.
                    accounts = contact.accounts.all()
                        account = accounts.first()
        elif account:
            user = account.assigned_to

            user = assignee
        if user:
            return {
                'internal_number': user.internal_number,
                'user': user,
            }

        return {}

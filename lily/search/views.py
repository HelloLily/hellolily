from datetime import date, timedelta

from django.db.models import Q
from django.http.response import HttpResponse
from django.views.generic.base import View

import anyjson
import freemail
from lily.accounts.models import Account, Website
from lily.cases.models import Case
from lily.deals.models import Deal
from lily.messaging.email.models.models import EmailAccount
from lily.utils.functions import parse_phone_number
from lily.utils.views.mixins import LoginRequiredMixin
from lily.search.functions import search_number

from .lily_search import LilySearch


class SearchView(LoginRequiredMixin, View):
    """
    Generic search view suitable for all models that have search enabled.
    """
    def get(self, request):
        """
        Parses the GET parameters to create a search

        Returns:
            HttpResponse with JSON dict:
                hits (list): dicts with search results per item
                total (int): total number of results
                took (int): milliseconds Elastic search took to get the results
        """
        kwargs = {}
        user = self.request.user

        model_type = request.GET.get('type')
        if model_type:
            kwargs['model_type'] = model_type
        sort = request.GET.get('sort')
        if sort:
            kwargs['sort'] = sort
        page = request.GET.get('page')
        if page:
            kwargs['page'] = int(page)
        size = request.GET.get('size')
        if size:
            kwargs['size'] = int(size)

        facet_field = request.GET.get('facet_field', '')
        facet_filters = request.GET.get('facet_filter', '')

        filters = []

        if facet_filters:
            facet_filters = facet_filters.split(',')

            for facet_filter in facet_filters:
                if facet_filter.split(':')[1]:
                    filters.append(facet_filter)

        facet_size = request.GET.get('facet_size', 60)
        if facet_field:
            kwargs['facet'] = {
                'field': facet_field,
                'filters': filters,
                'size': facet_size,
            }

        # Passing arguments as **kwargs means we can use the defaults.
        search = LilySearch(
            tenant_id=request.user.tenant_id,
            **kwargs
        )

        id_arg = request.GET.get('id', '')
        if id_arg:
            search.get_by_id(id_arg)

        query = request.GET.get('q', '').lower()
        if query:
            search.query_common_fields(query)

        account_related = request.GET.get('account_related', '')
        if account_related:
            search.account_related(int(account_related))

        contact_related = request.GET.get('contact_related', '')
        if contact_related:
            search.contact_related(int(contact_related))

        user_email_related = request.GET.get('user_email_related', '')
        if user_email_related:
            search.user_email_related(user)

        filterquery = request.GET.get('filterquery', '')
        if filterquery:
            search.filter_query(filterquery)

        return_fields = filter(None, request.GET.get('fields', '').split(','))
        if '*' in return_fields:
            return_fields = None

        hits, facets, total, took = search.do_search(return_fields)

        if model_type == 'email_emailmessage':
            email_accounts = EmailAccount.objects.filter(tenant=user.tenant).distinct('id')

            filtered_hits = []

            for hit in hits:
                try:
                    email_account = email_accounts.get(pk=hit.get('account').get('id'))
                except EmailAccount.DoesNotExist:
                    pass
                else:
                    # Check if the user has full access to the email messages.
                    # This means the user is either the owner or the email account has been shared with him/her.
                    is_owner = email_account.owner == user
                    shared_with = (user.id in email_account.shared_with_users.values_list('id', flat=True))
                    has_full_access = (is_owner or shared_with)

                    print email_account.privacy

                    # If the email account is set to metadata only, just set these fields.
                    if (email_account.privacy == EmailAccount.METADATA and not has_full_access):
                        filtered_hits.append({
                            'sender_name': hit.get('sender_name'),
                            'sender_email': hit.get('sender_email'),
                            'subject': hit.get('sender'),
                            'received_by_email': hit.get('received_by_email'),
                            'received_by_name': hit.get('received_by_name'),
                            'received_by_cc_email': hit.get('received_by_cc_email'),
                            'received_by_cc_name': hit.get('received_by_cc_name'),
                            'sent_date': hit.get('sent_date'),
                        })
                    elif email_account.privacy == EmailAccount.PRIVATE and not has_full_access:
                        # Private email (account), so don't add to list.
                        pass
                    else:
                        filtered_hits.append(hit)

                    hits = filtered_hits

        results = {'hits': hits, 'total': total, 'took': took}

        if facets:
            results['facets'] = facets

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')


class EmailAddressSearchView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        email_address = kwargs.get('email_address', None)

        results = {}

        # Only search for contacts if a full email is given.
        if email_address.split('@')[0]:
            # Search for contact with given email address.
            results = self._search_contact(email_address)

        # Don't continue search if we're dealing with a free email address.
        if freemail.is_free(email_address):
            results.update({
                'free_mail': True,
            })
        else:
            # Search for account with given email address.
            if not results:
                results = self._search_account(email_address)

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

    def _search_contact(self, email_address):
        """
        Search for contact with given email address.

        Args:
            email_address (string): string representation of an email address

        Returns:
            dict with search results or empty dict
        """
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='contacts_contact',
            size=1,
        )
        # Try to find an contact with the full email address.
        search.filter_query('email_addresses.email_address:"%s"' % email_address)

        hits, facets, total, took = search.do_search()
        if hits:
            return {
                'type': 'contact',
                'data': hits[0],
            }
        return {}

    def _search_account(self, email_address):
        """
        Search for account with given email address.

        Args:
            email_address (string): string representation of an email address

        Returns:
            dict with search results or empty dict
        """
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='accounts_account',
            size=1,
        )
        # Try to find an account with the full email address.
        search.filter_query('email_addresses.email_address:"%s"' % email_address)

        hits, facets, total, took = search.do_search()
        if hits:
            return {
                'type': 'account',
                'data': hits[0],
                'complete': True,
            }
        else:
            search = LilySearch(
                tenant_id=self.request.user.tenant_id,
                model_type='accounts_account',
                size=1,
            )

            # No account with the full email address exist, so use the domain for further searching.
            domain = email_address.split('@')[1]
            second_level_domain = Website(website=domain).second_level

            # Try to find an account which contains the domain.
            search.filter_query('email_addresses.email_address:"%s" OR second_level_domain:"%s"' %
                                (domain, second_level_domain))

            hits, facets, total, took = search.do_search()
            if hits:
                return {
                    'type': 'account',
                    'data': hits[0],
                    'complete': False,
                }

        return {}


class WebsiteSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        website = kwargs.get('website', None)
        results = self._search_website(website)

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

    def _search_website(self, website):
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='accounts_account',
            size=1,
        )
        # Try to find an account with the given website.
        search.filter_query('domain:%s' % website)

        hits, facets, total, took = search.do_search()
        if hits:
            return {
                'type': 'website',
                'data': hits[0],
                'complete': True,
            }

        return {}


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

        results = search_number(self.request.user.tenant_id, number)

        # Return only the primary keys of the accounts and contacts
        for account in results['data']['accounts']:
            response['data']['accounts'].append(account.id)

        for contact in results['data']['contacts']:
            response['data']['contacts'].append(contact.id)

        return HttpResponse(anyjson.dumps(response), content_type='application/json; charset=utf-8')


class InternalNumberSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        number = kwargs.get('number', None)

        if number:
            # For now we'll always convert the phone number to a certain format.
            # In the future we might change how we handle phone numbers.
            number = parse_phone_number(number)

        results = self._search_number(number)

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

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
        # Try to find a contact with the given phone number.
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='contacts_contact',
            size=1,
        )
        search.filter_query('phone_numbers.number:"%s"' % number)

        hits, facets, total, took = search.do_search()

        user = {}

        if hits[0]:
            contact = hits[0]

        week_ago = date.today() - timedelta(days=7)

        if contact:
            accounts = contact.get('accounts')

            cases = Case.objects.filter(contact=contact.get('id'), is_deleted=False).order_by('-modified')
            open_case = cases.filter(status__name='New').first()

            deals = Deal.objects.filter(
                contact=contact.get('id'),
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
                    if accounts:
                        # None of the above applies, so use account if possible.
                        account = Account.objects.get(pk=accounts[0].get('id'))
                        user = account.assigned_to
        else:
            if accounts:
                # None of the above applies, so use account if possible.
                account = Account.objects.get(pk=accounts[0].get('id'))
                user = account.assigned_to

        if user:
            return {
                'internal_number': user.internal_number,
                'user': user.id,
            }

        return {}

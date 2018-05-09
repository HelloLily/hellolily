from datetime import date, timedelta

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.response import HttpResponse
from django.views.generic.base import View

import anyjson
import freemail
from lily.accounts.models import Account, Website
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.messaging.email.models.models import EmailAccount
from lily.utils.functions import parse_phone_number
from lily.search.functions import search_number
from lily.utils.models.models import PhoneNumber

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
            content_type = ContentType.objects.get(app_label='email', model='emailmessage')
            email_accounts = EmailAccount.objects.filter(
                tenant=user.tenant,
                is_deleted=False,
                is_active=True,
            ).distinct('id')

            if user.tenant.billing.is_free_plan:
                email_accounts = email_accounts.filter(
                    owner=user,
                )

            filtered_hits = []

            for hit in hits:
                hit.update({
                    'content_type': content_type.id,
                })

                try:
                    email_account = email_accounts.get(pk=hit.get('account').get('id'))
                except EmailAccount.DoesNotExist:
                    pass
                else:
                    shared_config = email_account.sharedemailconfig_set.filter(user=user).first()

                    # If the email account or sharing is set to metadata only, just return these fields.
                    metadata_only_message = {
                        'id': hit.get('id'),
                        'sender_name': hit.get('sender_name'),
                        'sender_email': hit.get('sender_email'),
                        'received_by_email': hit.get('received_by_email'),
                        'received_by_name': hit.get('received_by_name'),
                        'received_by_cc_email': hit.get('received_by_cc_email'),
                        'received_by_cc_name': hit.get('received_by_cc_name'),
                        'sent_date': hit.get('sent_date'),
                        'privacy': hit.get('account').get('privacy'),
                    }

                    if email_account.owner == user:
                        filtered_hits.append(hit)
                    else:
                        if shared_config:
                            privacy = shared_config.privacy
                        else:
                            privacy = email_account.privacy

                        metadata_only_message.update({
                            'privacy': privacy,
                        })

                        if privacy == EmailAccount.METADATA:
                            filtered_hits.append(metadata_only_message)
                        elif privacy == EmailAccount.PRIVATE:
                            # Private email (account), so don't add to list.
                            continue
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

        response = {
            'data': {
            },
        }

        account, contact = search_number(self.request.user.tenant_id, number)

        if account:
            response['data']['account'] = {'id': account.id, 'name': account.name}

        if contact:
            response['data']['contact'] = {'id': contact.id, 'name': contact.full_name}

        return HttpResponse(anyjson.dumps(response), content_type='application/json; charset=utf-8')


class InternalNumberSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        phone_number = kwargs.get('number', None)

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

            deal = Deal.objects.filter(
                tenant=tenant,
                account=account,
                contact__isnull=False,
                is_deleted=False
            ).order_by(
                '-modified'
            ).first()

            if case:
                contact = case.contact
                assignee = case.assigned_to
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

        user = None
        assignee = None

        phone_numbers = PhoneNumber.objects.filter(
            tenant=tenant,
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
                    if accounts:
                        account = accounts.first()
                        user = account.assigned_to
        elif account:
            user = account.assigned_to

        if not user and assignee:
            user = assignee

        if user:
            return {
                'internal_number': user.internal_number,
                'user': user,
            }

        return {}

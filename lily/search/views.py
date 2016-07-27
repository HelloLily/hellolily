import anyjson
import freemail
from django.http.response import HttpResponse
from django.views.generic.base import View

from lily.accounts.models import Website
from lily.utils.views.mixins import LoginRequiredMixin

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
        facet_filter = request.GET.get('facet_filter', '')
        facet_size = request.GET.get('facet_size', 60)
        if facet_field:
            kwargs['facet'] = {
                'field': facet_field,
                'filter': facet_filter,
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
            search.user_email_related(self.request.user)

        filterquery = request.GET.get('filterquery', '')
        if filterquery:
            search.filter_query(filterquery)

        return_fields = filter(None, request.GET.get('fields', '').split(','))
        if '*' in return_fields:
            return_fields = None

        hits, facets, total, took = search.do_search(return_fields)

        results = {'hits': hits, 'total': total, 'took': took}

        if facets:
            results['facets'] = facets

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')


class EmailAddressSearchView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        email_address = kwargs.get('email_address', None)

        results = {}

        if not freemail.is_free(email_address):
            # Only search for contacts if a full email is given.
            if email_address.split('@')[0]:
                # 1: Search for contact with given email address.
                results = self._search_contact(email_address)

            # 2: Search for account with given email address.
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

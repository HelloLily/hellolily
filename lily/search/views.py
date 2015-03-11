import anyjson
from django.http.response import HttpResponse
from django.views.generic.base import View

from lily.utils.views.mixins import LoginRequiredMixin

from .utils import LilySearch


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

        user_email_related = request.GET.get('user_email_related', '')
        if user_email_related:
            search.user_email_related(self.request.user)

        filterquery = request.GET.get('filterquery', '')
        if filterquery:
            search.filter_query(filterquery)

        return_fields = filter(None, request.GET.get('fields', '').split(','))
        if '*' in return_fields:
            return_fields = None
        hits, total, took = search.do_search(return_fields)

        results = {'hits': hits, 'total': total, 'took': took}
        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')


class EmailAddressSearchView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        email_address = kwargs.get('email_address', None)

        # 1: Search for Contact with given email address
        results = self._search_contact(email_address)

        # 2: Search for Account with given email address
        if not results:
            results = self._search_account(email_address)

        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

    def _search_contact(self, email_address):
        """
        Search for contact with given email address.

        Args:
            email_address (string): string representation of an email address

        Returns:
            dict with search results empty dict
        """
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='contacts_contact',
            size=1,
        )
        search.filter_query('email:%s' % email_address)

        hits, total, took = search.do_search()
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
            dict with search results empty dict
        """
        search = LilySearch(
            tenant_id=self.request.user.tenant_id,
            model_type='accounts_account',
            size=1,
        )
        search.filter_query('email:%s' % email_address)

        hits, total, took = search.do_search()
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
            search.filter_query('email:%s' % email_address.split('@')[1])

            hits, total, took = search.do_search()
            if total > 1:
                return {}
            if hits:
                return {
                    'type': 'account',
                    'data': hits[0],
                    'complete': False,
                }

        return {}

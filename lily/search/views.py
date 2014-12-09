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
            JSON dict:
                hits (list): dicts with search results per item
                total (int): total number of results
                took (int): milliseconds Elastic search took to get the results
        """
        tenant_id = request.user.tenant_id
        id_arg = request.GET.get('id', '')
        model_type = request.GET.get('type', '')
        sort = request.GET.get('sort', '')
        page = int(request.GET.get('page', '0'))
        page = 0 if page < 0 else page
        size = int(request.GET.get('size', '10'))
        size = 1 if size < 1 else size
        return_fields = filter(None, request.GET.get('fields', '').split(','))
        if '*' in return_fields:
            return_fields = ''

        search = LilySearch(
            tenant_id=tenant_id,
            id_arg=id_arg,
            model_type=model_type,
            sort=sort,
            page=page,
            size=size,
        )

        hits, total, took = [], 0, 0

        query = request.GET.get('q', '').lower()
        filter_query = request.GET.get('filterquery', '')

        if 'q' in request.GET:
            hits, total, took = search.raw_query(
                query=query,
                return_fields=return_fields,
            )

        elif 'filterquery' in request.GET:
            hits, total, took = search.filter_query(
                filterquery=filter_query,
                return_fields=return_fields,
            )

        results = {'hits': hits, 'total': total, 'took': took}
        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

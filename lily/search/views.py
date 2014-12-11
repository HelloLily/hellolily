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
            search.raw_query(query)

        filterquery = request.GET.get('filterquery', '')
        if filterquery:
            search.filter_query(filterquery)

        return_fields = filter(None, request.GET.get('fields', '').split(','))
        if '*' in return_fields:
            return_fields = None
        hits, total, took = search.do_search(return_fields)

        results = {'hits': hits, 'total': total, 'took': took}
        return HttpResponse(anyjson.dumps(results), content_type='application/json; charset=utf-8')

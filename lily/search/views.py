import anyjson
from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic.base import View
from elasticutils import S

from lily.utils.views.mixins import LoginRequiredMixin


class SearchView(LoginRequiredMixin, View):
    '''
    Generic search view suitable for all models that have search enabled.
    '''
    def get(self, request):
        query = request.GET.get('q', '')
        tenant = request.user.tenant_id
        modeltype = request.GET.get('type', '')
        results = {'hits': [], 'query': {'q': query, 'type': modeltype}}

        search_request = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES['default'])
        search = search_request.all().order_by('-modified')

        if modeltype:
            search = search.filter(_type=modeltype)

        if query:
            search = search.filter(name=query, tenant=tenant)
        for result in search.execute():
            results['hits'].append({'id': result.id, 'name': result.name})
        return HttpResponse(anyjson.dumps(results), mimetype='application/json')

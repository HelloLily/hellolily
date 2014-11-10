import anyjson
from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic.base import View
from elasticutils import S

from lily.utils.views.mixins import LoginRequiredMixin


class SearchView(LoginRequiredMixin, View):
    """
    Generic search view suitable for all models that have search enabled.
    """
    def get(self, request):
        search_request = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES['default'])
        search = search_request.all()
        raw_filters = []

        tenant = request.user.tenant_id
        search = search.filter(tenant=tenant)

        query = request.GET.get('q', '')
        for token in query.split(' '):
            if token:
                search = search.filter(or_={'name': token.lower(),
                                            'phone': token.lower()})

        id_arg = request.GET.get('id', '')
        if id_arg:
            raw_filters.append({'ids': {'values': [id_arg]}})

        for int_field in ['account', 'contact']:
            get_value = request.GET.get(int_field, '')
            if get_value:
                if get_value == '*':
                    raw_filters.append(self.get_exists_filter(int_field))
                else:
                    search = search.filter(or_={int_field: get_value})

        for string_field in ['name', 'phone', 'email', 'tag']:
            get_value = request.GET.get(string_field, '')
            if get_value:
                if get_value == '*':
                    raw_filters.append(self.get_exists_filter(string_field))
                else:
                    search = search.filter(or_={string_field: get_value.lower()})

        modeltype = request.GET.get('type', '')
        if modeltype:
            search = search.doctypes(modeltype)

        sort = request.GET.get('sort', '-modified')
        if sort:
            search = search.order_by(sort)

        page = int(request.GET.get('page', '0'))
        page = 0 if page < 0 else page
        size = int(request.GET.get('size', '10'))
        size = 1 if size < 1 else size
        from_hits = page * size
        to_hits = (page + 1) * size
        search = search[from_hits:to_hits]

        if raw_filters:
            search = search.filter_raw({'and': raw_filters})

        # Execute the search, process the hits and return as json.
        return_fields = filter(None, request.GET.get('fields', '').split(','))
        if '*' in return_fields:
            return_fields = ''
        hits = []
        execute = search.execute()
        for result in execute:
            hit = {
                'id': result.id,
            }
            if not modeltype:
                # We will add type if not specifically searched on it.
                hit['type'] = result.es_meta.type
            for field in result:
                # Add specified fields, or all fields when not specified
                if return_fields:
                    if field in return_fields:
                        hit[field] = result[field]
                else:
                    hit[field] = result[field]
            hits.append(hit)

        results = {'hits': hits, 'total': execute.count, 'took': execute.took}
        return HttpResponse(anyjson.dumps(results), mimetype='application/json; charset=utf-8')

    def get_exists_filter(self, filter_name):
        return {'exists': {'field': filter_name}}

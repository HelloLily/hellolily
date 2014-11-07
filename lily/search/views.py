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
        search_request = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES['default'])
        search = search_request.all()
        raw_filters = []

        tenant = request.user.tenant_id
        search = search.filter(tenant=tenant)

        query = request.GET.get('q', '')
        if query:
            search = search.filter(name=query)

        id_arg = request.GET.get('id', '')
        if id_arg:
            raw_filters.append({'ids': {'values': [id_arg]}})

        account = request.GET.get('account', '')
        if account:
            if account == '*':
                raw_filters.append(self.get_exists_filter(account))
            else:
                search = search.filter(account=account)

        contact = request.GET.get('contact', '')
        if contact:
            if contact == '*':
                raw_filters.append(self.get_exists_filter(contact))
            else:
                search = search.filter(contact=contact)

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
        hits = []
        execute = search.execute()
        for result in execute:
            hit = {
                'id': result.id,
                'name': result.name,
            }
            if not modeltype:
                # We will add type if not specifically searched on it.
                hit['type'] = result.es_meta.type
            if 'account' in result:
                hit['account'] = result.account
            if 'contact' in result:
                hit['contact'] = result.contact
            hits.append(hit)

        results = {'hits': hits, 'total': execute.count}
        if settings.DEBUG or request.GET.get('debug'):
            # Only add non sensitive information.
            results['debug'] = {
                'tenant': tenant,
                'q': query,
                'type': modeltype,
                'page': page,
                'size': size,
                'took': execute.took,
                'sort': sort,
            }
        return HttpResponse(anyjson.dumps(results), mimetype='application/json')

    def get_exists_filter(self, filter_name):
        return {'exists': {'field': filter_name}}

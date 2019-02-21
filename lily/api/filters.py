from elasticsearch_dsl.query import MultiMatch
from rest_framework.filters import SearchFilter, BaseFilterBackend
from rest_framework.settings import api_settings
from lily.search.lily_search import LilySearch


class ElasticSearchFilter(BaseFilterBackend):
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        if params:
            return params.split(',')
        return None

    def filter_queryset(self, request, queryset, view):
        model_type = getattr(view, 'model_type', None)

        if not model_type:
            return queryset

        search_terms = self.get_search_terms(request)

        if not search_terms:
            return queryset

        if 'limit' in request.query_params:
            limit = request.query_params['limit']

            search = LilySearch(
                tenant_id=request.user.tenant_id,
                model_type=model_type,
                size=int(limit),
            )
        else:
            search = LilySearch(
                tenant_id=request.user.tenant_id,
                model_type=model_type,
            )

        search.filter_query(' AND '.join(search_terms))
        ids = [result['id'] for result in search.do_search(['id'])[0]]

        return queryset.filter(id__in=ids)


class NewElasticSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        if not hasattr(queryset, 'elasticsearch_query'):
            raise AttributeError('ElasticSearchFilter can only be used with an ElasticQuerySet.')

        search_fields = getattr(view, 'search_fields', None)
        search_term = request.query_params.get(self.search_param, '')

        if not search_fields or not search_term:
            return queryset

        fields = [field.replace('__', '.') for field in search_fields]
        ngram_fields = ['{}.{}'.format(field, 'ngram') for field in fields]

        return queryset.elasticsearch_query(MultiMatch(
            query=search_term,
            fields=fields + ngram_fields,
            type='most_fields',
            operator='and',
            fuzziness='AUTO'
        ))

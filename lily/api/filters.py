from elasticsearch_dsl.query import MultiMatch
from rest_framework.filters import SearchFilter


class ElasticSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        if not hasattr(queryset, 'elasticsearch_query'):
            raise AttributeError('ElasticSearchFilter can only be used with an ElasticQuerySet.')

        search_fields = getattr(view, 'search_fields', None)
        search_term = request.query_params.get(self.search_param, '')

        if not search_fields or not search_term:
            return queryset

        fields = [field.replace('__', '.') for field in search_fields]

        return queryset.elasticsearch_query(MultiMatch(
            query=search_term,
            fields=fields,
            type='most_fields',
            operator='and',
            fuzziness='AUTO'
        ))

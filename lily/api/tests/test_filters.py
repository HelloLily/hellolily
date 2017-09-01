from unittest import TestCase

from django.test import RequestFactory
from faker import Faker
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.cases.models import Case
from lily.search.models import ElasticQuerySet


class ElasticSearchFilterTest(TestCase):

    def setUp(self):
        super(ElasticSearchFilterTest, self).setUp()
        self.request_factory = RequestFactory()

    def _get_elastic_query_set(self):
        return Case.elastic_objects.all()

    def test_filter_queryset(self):
        """
        Test filter_queryset adds a MultiMatch query to the set.
        """
        search_term = Faker().sentence()
        qs = self._get_elastic_query_set()
        request = self.request_factory.get('/api/model')
        request.query_params = {'search': search_term}

        view = ModelViewSet()
        view.search_fields = ('name', 'description', 'tag__name', )

        new_qs = ElasticSearchFilter().filter_queryset(request, qs, view)

        expected_query = {
            'multi_match': {
                'operator': 'and',
                'fields': ['name', 'description', 'tag.name'],
                'type': 'most_fields',
                'fuzziness': 'AUTO',
                'query': search_term,
            }
        }

        self.assertEqual(expected_query, new_qs.search.to_dict().get('query', {}))

    def test_filter_queryset_no_search(self):
        """
        Test filter_queryset doesn't search without search param.
        """
        qs = self._get_elastic_query_set()
        request = self.request_factory.get('/api/model')
        request.query_params = {'search': ''}

        view = ModelViewSet()
        view.search_fields = ('name', 'description', 'tag__name', )

        new_qs = ElasticSearchFilter().filter_queryset(request, qs, view)

        self.assertEqual({'match_all': {}}, new_qs.search.to_dict().get('query', {}))

    def test_filter_queryset_requires_elastic_queryset(self):
        """
        Test filter_queryset returns an error with incompatible queryset.
        """
        qs = Case.objects.all()
        self.assertNotIsInstance(qs, ElasticQuerySet)

        request = self.request_factory.get('/api/model')
        request.query_params = {'search': ''}

        view = ModelViewSet()
        view.search_fields = ('name', 'description', 'tag__name', )

        with self.assertRaises(AttributeError):
            ElasticSearchFilter().filter_queryset(request, qs, view)

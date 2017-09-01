import logging
import time

from django.test.testcases import TestCase
from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, MultiMatch
from mock import MagicMock

from lily.cases.factories import CaseFactory
from lily.cases.models import Case
from lily.search.models import ElasticQuerySet

logger = logging.getLogger(__name__)


def wait_for_search_results(model, query):
    doc_type = list(registry.get_documents([model.__class__]))[0]
    index = Index(doc_type._doc_type.index)

    for i in range(0, 5):
        response = doc_type.search().query(query).execute(ignore_cache=True)
        ids = [hit.meta.id for hit in response.hits]

        if model.id in ids:
            break

        logger.warning('Waiting for Elasticsearch index to update... (%ds)' % (i + 1))
        index.refresh()
        time.sleep(1)


class ElasticQuerySetTestCase(TestCase):
    model_class = Case
    search_field = 'subject'

    @classmethod
    def setUpTestData(cls):
        super(ElasticQuerySetTestCase, cls).setUpTestData()
        cls.model_instance = CaseFactory.create()

    def get_query_set_with_full_text_search(self):
        return ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))

    def test_init(self):
        """
        ElasticQuerySet init creates a new search object.
        """
        qs = ElasticQuerySet(self.model_class)

        self.assertIsInstance(qs.search, Search)

    def test__has_full_text_search_no_search(self):
        """
        _has_full_text_search returns false if the QS lacks full text search.
        """
        self.assertFalse(ElasticQuerySet().has_full_text_search)

    def test__has_full_text_search_match(self):
        """
        _has_full_text_search returns true if the QS has a match query.
        """
        self.assertTrue(ElasticQuerySet(self.model_class).elasticsearch_query(Match(foo='bar')).has_full_text_search)

    def test__has_full_text_search_multi_match(self):
        """
        _has_full_text_search returns true if the QS has a multi match query.
        """
        self.assertTrue(self.get_query_set_with_full_text_search().has_full_text_search)

    def test__has_full_text_search_filter(self):
        """
        _has_full_text_search returns false if the QS has a filter query.
        """
        qs = ElasticQuerySet(self.model_class)
        qs.search = qs.search.filter(foo='bar')

        self.assertFalse(qs.has_full_text_search)

    def test__has_full_text_search_filter_multi_match(self):
        """
        _has_full_text_search returns true if QS has filter and match query.
        """
        qs = self.get_query_set_with_full_text_search()
        qs.search = qs.search.filter(fux='baz')

        self.assertTrue(qs.has_full_text_search)

    def test_first_uses_elasticsearch_for_full_text(self):
        """
        first uses Elasticsearch if the query has full text search.
        """
        query = Match(**{self.search_field: getattr(self.model_instance, self.search_field)})

        wait_for_search_results(self.model_instance, query)

        qs = ElasticQuerySet(self.model_class).elasticsearch_query(query)
        qs.search.execute = MagicMock(wraps=qs.search.execute)

        result = qs.first()

        qs.search.execute.assert_called_once_with(ignore_cache=True)

        self.assertEqual(self.model_instance, result)

    def test_first_uses_sql_without_full_text_search(self):
        """
        first doesn't use Elasticsearch if there is no full text search.
        """
        qs = ElasticQuerySet(self.model_class)
        qs.search.execute = MagicMock(wraps=qs.search.execute)

        qs.first()

        qs.search.execute.assert_not_called()

    def test_last_full_text_search(self):
        """
        last cannot be used with full text search.
        """
        qs = ElasticQuerySet(self.model_instance.__class__).elasticsearch_query(
            Match(foo='bar')
        )
        self.assertRaises(NotImplementedError, qs.last)

    def test_last_no_search(self):
        """
        last can be used without full text search.
        """
        qs = ElasticQuerySet(self.model_class)
        self.assertIsNotNone(qs.filter(pk=self.model_instance.pk).last())

    def test_count_uses_elasticsearch_full_text(self):
        """
        count uses Elasticsearch if a query has full text search.
        """
        qs = ElasticQuerySet(self.model_class).elasticsearch_query(MultiMatch(query='test', fields=['foo', 'bar']))
        qs.search.execute = MagicMock(wraps=qs.search.execute)
        qs.query.get_count = MagicMock(wraps=qs.query.get_count)

        qs.count()

        qs.search.execute.assert_called_once()
        qs.query.get_count.assert_not_called()

    def test_count_uses_sql_without_full_text(self):
        """
        count uses SQL if a query does not have full text search.
        """
        qs = ElasticQuerySet(self.model_class)
        qs.search.execute = MagicMock(wraps=qs.search.execute)
        qs.query.get_count = MagicMock(wraps=qs.query.get_count)

        qs.count()

        qs.search.execute.assert_not_called()
        qs.query.get_count.assert_called_once()

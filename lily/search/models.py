from django.db import models
from django.db.models import Manager
from django.db.models.query_utils import Q
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Term

from lily.tenant.middleware import get_current_user


class ElasticQuerySet(models.QuerySet):
    """
    Override the default QuerySet with Elasticsearch capabilities.
    """

    def __init__(self, model=None, query=None, using=None, hints=None, search=None):
        super(ElasticQuerySet, self).__init__(model=model, query=query, using=using, hints=hints)
        if search is None:
            doc_types = registry.get_documents([model])

            search = Search(
                index=[doc_type._doc_type.index for doc_type in doc_types],
                doc_type=list(doc_types)
            ).source(include=[])[0:10000]
        self.search = search
        self._total = None

    def _sql_iterator(self):
        """
        Use the base QuerySet iterator() method to get results from the DB.

        Returns:
            iter: An iterator over the database results.
        """
        return super(ElasticQuerySet, self).iterator()

    @property
    def has_full_text_search(self):
        """
        Check whether this queryset has any full text search queries.

        Elasticsearch DSL wraps every search in a bool query. These queries
        typically have two components: a `filter` component and a `must`
        component for full text search. To figure out if such a component,
        check the search dict for search['query']['bool']['must'].

        Returns:
            bool: True if any full text queries are present, False otherwise.
        """
        search_dict = self.search.to_dict()

        return (('must' in search_dict.get('query', {}).get('bool', {})) or
                ('match' in search_dict.get('query', {})) or
                ('multi_match' in search_dict.get('query', {})))

    def _fetch_all(self):
        """
        Fetch all models from the database based on the Elasticsearch results.

        Populates self._result_cache with a list of models from the
        Elasticsearch results.
        """
        if self._result_cache is None:
            if self.has_full_text_search:
                response = self.search.execute(ignore_cache=True)
                self._total = response.hits.total
                ids = [hit.meta.id for hit in response.hits]

                obj = self._clone()
                obj.query.add_q(Q(pk__in=ids))
                models = {obj._get_pk_val(): obj for obj in obj._sql_iterator()}

                self._result_cache = [models[int(idx)] for idx in ids if int(idx) in models]
            else:
                self._result_cache = list(self._sql_iterator())
                self._total = super(ElasticQuerySet, self).count()

        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()

    def count(self):
        """
        Count the total number of objects matching this query.

        Unlike in the regular QuerySet, it's not possible to do a count query
        in Elasticsearch.

        Returns:
            int: The number of objects.
        """
        if self._total is not None:
            return self._total
        elif self.has_full_text_search:
            self._fetch_all()
            return self._total
        else:
            return super(ElasticQuerySet, self).count()

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        clone = self.filter(*args, **kwargs)
        if self.query.can_filter():
            clone = clone.order_by()

        results = list(clone._sql_iterator())

        num = len(results)
        if num == 1:
            return results[0]
        if not num:
            raise self.model.DoesNotExist(
                "%s matching query does not exist." %
                self.model._meta.object_name
            )
        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s!" %
            (self.model._meta.object_name, num)
        )

    def first(self):
        """
        Returns the first object of a query, returns None if no match is found.
        """
        if self.has_full_text_search:
            if not self._result_cache:
                self._fetch_all()

            return self._result_cache[0] if len(self._result_cache) > 0 else None
        else:
            return super(ElasticQuerySet, self).first()

    def last(self):
        if self.has_full_text_search:
            raise NotImplementedError('Elasticsearch does not support last queries.')
        else:
            return super(ElasticQuerySet, self).last()

    def _clone(self, klass=None, setup=False, **kwargs):
        """
        Clone the QuerySet but preserve the Elasticsearch Search request.
        """
        obj = super(ElasticQuerySet, self)._clone(klass=klass, setup=setup, **kwargs)
        obj.search = self.search
        return obj

    def elasticsearch_query(self, *args, **kwargs):
        """
        Add an Elasticsearch query object to the QuerySet.

        Useful when utilizing the full text search capabilities of
        Elasticsearch outside the QuerySet API.

        Returns:
            ElasticQuerySet: The query set with updated search query.
        """
        obj = self._clone()
        obj.search = obj.search.query(*args, **kwargs)
        return obj


class ElasticTenantManager(Manager.from_queryset(ElasticQuerySet)):
    def get_queryset(self):
        """
        Manipulate the returned queryset by adding a filter for tenant using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        user = get_current_user()
        if user and user.is_authenticated():
            qs = super(ElasticTenantManager, self).get_queryset().filter(tenant_id=user.tenant_id)
            return qs.elasticsearch_query(Term(tenant_id=user.tenant_id))
        else:
            return super(ElasticTenantManager, self).get_queryset()

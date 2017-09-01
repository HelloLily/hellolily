from __future__ import absolute_import, unicode_literals

from django_elasticsearch_dsl.management.commands.search_index import Command as SearchIndexCommand
from elasticsearch_dsl.connections import connections

connection = connections.get_connection()


class Command(SearchIndexCommand):
    # Just reuse the Django Elasticsearch DSL command for now,
    # pending rewrite.
    pass

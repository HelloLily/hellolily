from django.utils.module_loading import autodiscover_modules
from django_elasticsearch_dsl.apps import DEDConfig
from elasticsearch_dsl.connections import connections

from lily.settings import settings


class SearchConfig(DEDConfig):
    name = 'lily.search'
    signal_processor = None

    def ready(self):
        autodiscover_modules('search')
        connections.configure(**settings.ELASTICSEARCH_DSL)

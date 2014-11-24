from optparse import make_option
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from elasticutils.contrib.django import get_es, tasks

from lily.search.analyzers import get_analyzers
from lily.utils.functions import get_class


class Command(BaseCommand):
    help = """Index current model instances into Elasticsearch. It does this by \
creating a new index, then changing the alias to point to the new index. \
(afterwards removing the old index)."""

    option_list = BaseCommand.option_list + (
        make_option('-u', '--url',
                    action='store',
                    dest='url',
                    default='',
                    help='Override the ES_URLS in settings.',
                    ),
    )

    # The mappings for models with 'is_deleted' properties.
    # If you add a mapping for a regular model, then some extra steps are needed
    # to make sure deletions are picked up (during this management command).
    # You can do this by comparing the list of PKs before and after.
    MAPPINGS = [get_class(kls) for kls in settings.ES_MODEL_MAPPINGS]

    def handle(self, *args, **options):
        url = options['url']
        if url:
            es = get_es(urls=[url])
        else:
            es = get_es()
        # We define some custom analyzers that our mappings can use.
        index_settings = {'mappings': {}, 'settings': get_analyzers()}

        # Retrieve the mappings for the index-enabled models.
        for mappingClass in self.MAPPINGS:
            model_name = mappingClass.get_mapping_type_name()
            index_settings['mappings'].update({model_name: mappingClass.get_mapping()})

        # Create a new index.
        new_index = 'index_%s' % (int(time.time()))
        es.indices.create(new_index, body=index_settings)
        self.index(new_index)

        # The default index name, (we will use as an alias).
        index_name = settings.ES_INDEXES['default']

        # Check if we have a current index.
        old_index = None
        aliases = es.indices.get_aliases(name=index_name)
        for key, value in aliases.iteritems():
            if value['aliases']:
                old_index = key

        # Change the alias to point to our new index, and remove the old index.

        self.stdout.write('Changing alias "%s" from old index "%s" to new index "%s"' %
                          (index_name, old_index, new_index))
        if old_index:
            es.indices.update_aliases({'actions':
                                       [{'remove': {'index': old_index, 'alias': index_name}},
                                        {'add': {'index': new_index, 'alias': index_name}}]})
            es.indices.delete(old_index)
        else:
            if es.indices.exists(index_name):
                # This is a corner case. There was no alias named index_name, but
                # an index index_name nevertheless exists, this only happens when the index
                # was already created (because of ES auto creation features).
                es.indices.delete(index_name)
            es.indices.update_aliases({'actions':
                                       [{'add': {'index': new_index, 'alias': index_name}}]})

        # Finally re-index one more time, to pick up updates that were written during our command.
        # Note that this models that do not use the DeletedMixin will not work this way.
        self.index(index_name)
        self.unindex(index_name)

    def index(self, index_name):
        """
        Index objects from our index-enabled models.
        """
        for mappingClass in self.MAPPINGS:
            model = mappingClass.get_model()
            self.stdout.write('Indexing %s from index %s' % (model, index_name))
            model_objs = model.objects.filter(is_deleted=False)
            model_ids = list(model_objs.values_list('pk', flat=True))
            if model_ids:
                tasks.index_objects(mappingClass, model_ids, index=index_name)

    def unindex(self, index_name):
        """
        Removing deleted objects from our index-enabled models.
        """
        for mappingClass in self.MAPPINGS:
            model = mappingClass.get_model()
            self.stdout.write('Removing deleted %s objects from index %s' % (model,
                                                                             index_name))
            model_objs = model.objects.filter(is_deleted=True)
            model_ids = list(model_objs.values_list('pk', flat=True))
            if model_ids:
                try:
                    tasks.unindex_objects(mappingClass, model_ids, index=index_name)
                except:
                    pass

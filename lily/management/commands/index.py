from optparse import make_option
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from lily.search.analyzers import get_analyzers
from lily.search.connections_utils import get_es_client, get_index_name
from lily.search.indexing import index_objects
from lily.search.scan_search import ModelMappings


class Command(BaseCommand):
    help = """Index current model instances into Elasticsearch. It does this by
creating a new index, then changing the alias to point to the new index.
(afterwards removing the old index). It uses 1 index per type.

It uses custom index implementation for fast and synchronous indexing.

There are basically two ways to use this command, the first to index all
configured mappings:

    index

The second way is to target a specific model:

    index -t contact

or with fully qualified name:

    index -t lily.contacts.models.Contact

It is possible to specify multiple models, using comma separation."""

    option_list = BaseCommand.option_list + (
        make_option('-t', '--target',
                    action='store',
                    dest='target',
                    default='',
                    help='Choose specific model targets, comma separated.'
                    ),
        make_option('-q', '--queries',
                    action='store_true',
                    dest='queries',
                    help='Show the queries that were executed during the command.'
                    ),
        make_option('-f', '--force',
                    action='store_true',
                    dest='force',
                    help='Force the creation of the new index, removing the old one (leftovers).'
                    ),
    )

    def handle(self, *args, **options):
        es = get_es_client()

        target = options['target']
        if target:
            targets = target.split(',')
        else:
            targets = []  # (meaning all)
        has_targets = targets != []

        self.stdout.write('Please remember that HelloLily needs to be in maintenance mode. '
                          '(Hit ctrl+c in 5 seconds to abort).')
        time.sleep(5)

        for mapping in ModelMappings.get_model_mappings().values():
            model = mapping.get_model()
            model_name = mapping.get_mapping_type_name()
            main_index_base = settings.ES_INDEXES['default']
            main_index = get_index_name(main_index_base, mapping)

            # Skip this model if there are specific targets and not specified.
            if has_targets and not self.model_targetted(model, targets):
                continue

            self.stdout.write('==> %s' % model_name)

            # Check if we currently have an index for this mapping.
            old_index = None
            aliases = es.indices.get_aliases(name=main_index)
            for key, value in aliases.iteritems():
                if value['aliases']:
                    old_index = key
                    self.stdout.write('Current index "%s"' % key)

            # Check any indices with no alias (leftovers from failed indexing).
            # Or it could be that it is still in progress,
            aliases = es.indices.get_aliases()
            for key, value in aliases.iteritems():
                if not key.endswith(model_name):
                    # Not the model we are looking after.
                    continue
                if key == main_index:
                    # This is an auto created index. Will be removed at end of command.
                    continue
                if not value['aliases']:
                    if options['force']:
                        self.stdout.write('Removing leftover "%s"' % key)
                        es.indices.delete(key)
                    else:
                        raise Exception('Found leftover %s, proceed with -f to remove.'
                                        ' Make sure indexing this model is not already running!' % key)

            # Create new index.
            index_settings = {
                'mappings': {
                    model_name: mapping.get_mapping()
                },
                'settings': {
                    'analysis': get_analyzers()['analysis'],
                    'number_of_shards': 1,
                }
            }
            temp_index_base = 'index_%s' % (int(time.time()))
            temp_index = get_index_name(temp_index_base, mapping)

            self.stdout.write('Creating new index "%s"' % temp_index)
            es.indices.create(temp_index, body=index_settings)

            # Index documents.
            self.index_documents(mapping, temp_index_base)

            # Switch aliases.
            if old_index:
                es.indices.update_aliases({
                    'actions': [
                        {'remove': {'index': old_index, 'alias': main_index}},
                        {'remove': {'index': old_index, 'alias': main_index_base}},
                        {'add': {'index': temp_index, 'alias': main_index}},
                        {'add': {'index': temp_index, 'alias': main_index_base}},
                    ]
                })
                self.stdout.write('Removing previous index "%s"' % old_index)
                es.indices.delete(old_index)
            else:
                if es.indices.exists(main_index):
                    # This is a corner case. There was no alias named index_name, but
                    # an index index_name nevertheless exists, this only happens when the index
                    # was already created (because of ES auto creation features).
                    self.stdout.write('Removing previous (presumably auto created) index "%s"' % main_index)
                    es.indices.delete(main_index)
                es.indices.update_aliases({
                    'actions': [
                        {'add': {'index': temp_index, 'alias': main_index}},
                        {'add': {'index': temp_index, 'alias': main_index_base}},
                    ]
                })
            self.stdout.write('')

        self.stdout.write('Indexing finished.')
        for remaining_target in targets:
            self.stdout.write('There was an unknown target specified: %s' % remaining_target)

        if options['queries']:
            from django.db import connection
            for query in connection.queries:
                print query

    def index_documents(self, mapping, temp_index_base):
        model = mapping.get_model()
        self.stdout.write('Indexing %s' % self.full_name(model))

        if mapping.has_deleted():
            model_objs = model.objects.filter(is_deleted=False)
        else:
            model_objs = model.objects.all()

        index_objects(mapping, model_objs, temp_index_base, print_progress=True)

    def model_targetted(self, model, specific_targets):
        """
        Check if the model is targetted for indexing.
        """
        for specific_target in list(specific_targets):
            if specific_target.lower() in [model.__name__.lower(), self.full_name(model).lower()]:
                specific_targets.remove(specific_target)
                return True
        return False

    def full_name(self, model):
        """
        Get the fully qualified name of a model.
        """
        return '%s.%s' % (model.__module__, model.__name__)

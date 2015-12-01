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

or with other names:

    index -t lily.contacts.models.Contact
    index -t contacts_contact

It is possible to specify multiple models, using comma separation."""

    option_list = BaseCommand.option_list + (
        make_option('-t', '--target',
                    action='store',
                    dest='target',
                    default='',
                    help='Choose specific model targets, comma separated (no added space after comma).'
                    ),
        make_option('-q', '--queries',
                    action='store_true',
                    dest='queries',
                    help='Show the queries that were executed during the command.'
                    ),
        make_option('-l', '--list',
                    action='store_true',
                    dest='list',
                    help='List available models to target.'
                    ),
    )

    def handle(self, *args, **options):
        es = get_es_client()

        if args:
            self.stdout.write('Aborting, unexpected arguments %s' % list(args))
            return

        if options['list']:
            self.stdout.write('Possible models to index:\n')
            for mapping in ModelMappings.get_model_mappings().values():
                self.stdout.write(mapping.get_mapping_type_name())
            return

        target = options['target']
        if target:
            targets = target.split(',')
        else:
            targets = []  # (meaning all)
        has_targets = targets != []

        self.stdout.write('Please remember that HelloLily needs to be in maintenance mode. \n\n')

        if has_targets:
            # Do a quick run to check if all targets are valid models.
            check_targets = list(targets)  # make a copy
            for target in check_targets:
                for mapping in ModelMappings.get_model_mappings().values():
                    if self.model_targetted(mapping, [target]):
                        check_targets.remove(target)
                        break
            if check_targets:
                self.stdout.write('Aborting, following targets not recognized: %s' % check_targets)
                return

        for mapping in ModelMappings.get_model_mappings().values():
            model_name = mapping.get_mapping_type_name()
            main_index_base = settings.ES_INDEXES['default']
            main_index = get_index_name(main_index_base, mapping)

            # Skip this model if there are specific targets and not specified.
            if has_targets and not self.model_targetted(mapping, targets):
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

    def model_targetted(self, mapping, specific_targets):
        """
        Check if the mapping is targetted for indexing.
        """
        model = mapping.get_model()
        model_short_name = model.__name__.lower()
        model_full_name = self.full_name(model).lower()
        model_mappings_name = mapping.get_mapping_type_name().lower()
        for target in specific_targets:
            if target.lower() in [model_short_name, model_full_name, model_mappings_name]:
                return True
        return False

    def full_name(self, model):
        """
        Get the fully qualified name of a model.
        """
        return '%s.%s' % (model.__module__, model.__name__)

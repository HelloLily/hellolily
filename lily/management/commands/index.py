import os
import traceback
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from slacker import Slacker

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
    index -t lily.contacts.models.contact
    index -t contacts_contact
    index -t lily.contacts

It is possible to specify multiple models, using comma separation."""

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            '--target',
            action='store',
            dest='target',
            default='',
            help='Choose specific model targets, comma separated (no added space after comma).'
        )
        parser.add_argument(
            '-q',
            '--queries',
            action='store_true',
            dest='queries',
            help='Show the queries that were executed during the command.'
        )
        parser.add_argument('-l', '--list', action='store_true', dest='list', help='List available models to target.')
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            dest='force',
            help='Force the creation of the new index, removing the old one (leftovers).'
        )

    def handle(self, *args, **kwargs):
        self.stdout.write('Please remember that Lily needs to be in maintenance mode. \n\n')

        try:
            self.handle_args(*args)
            self.handle_kwargs(**kwargs)

            self.es = get_es_client()
            self.index()

            if self.log_queries:
                for query in connection.queries:
                    print query
        except Exception, e:
            self.stderr.write('\nIndexing error.\n')
            traceback.print_exc()

            heroku_env = os.environ.get('HEROKU_ENV')
            if heroku_env == 'production':
                travis_build = os.environ.get('TRAVIS_BUILD_ID')
                travis_link = 'https://travis-ci.org/HelloLily/hellolily/builds/{0}'.format(travis_build)
                slack = Slacker(os.environ.get('SLACK_API_TOKEN'))
                slack.chat.post_message(
                    '#lily_ci', 'Indexing failed with reason `{0}` in Travis build {1}.'.format(repr(e), travis_link)
                )

    def handle_args(self, *args):
        """
        Validate the arguments given, this command doesn't support arguments for now.
        """
        if args:
            self.stdout.write('Aborting, unexpected arguments %s' % list(args))
            return

    def handle_kwargs(self, **kwargs):
        """
        Validate the keyword argument given and prepare for indexing.
        Django makes sure there are no unspecified kwargs are passed to the command.
        """
        # Validate the list kwarg.
        self.list_mappings = kwargs['list'] is True

        # Validate the targets kwarg.
        targets_to_check = []
        if kwargs['target']:
            targets_to_check = kwargs['target'].split(',')

        # Validate the targets kwarg, every one of them should be known.
        self.validate_targets(targets_to_check)

        # Validate the queries kwarg.
        self.log_queries = kwargs['queries'] is True

        # Validate the force kwarg.
        self.force = kwargs['force'] is True

    def validate_targets(self, targets_to_check):
        """
        Validate every target that is passed to the command.
        """
        invalid_targets = []
        target_list = []

        if len(targets_to_check) == 1 and targets_to_check[0] == 'all_but_mail':
            all_targets = ModelMappings.app_to_mappings.keys()
            target_list += [
                ModelMappings.app_to_mappings[target] for target in all_targets if target != 'lily.messaging.email'
            ]
        else:
            for target in targets_to_check:
                if target in ModelMappings.app_to_mappings.keys():
                    # Target is an app.
                    target_list.append(ModelMappings.app_to_mappings[target])
                    continue

                for mapping in ModelMappings.mappings:
                    if target == mapping.get_mapping_type_name():
                        target_list.append(mapping)
                        break
                else:
                    # Only check this if the previous for loop didn't break.
                    for model, mapping in ModelMappings.model_to_mappings.items():
                        if target in [
                            model.__name__.lower(), '{0}.{1}'.format(model.__module__, model.__name__).lower()
                        ]:
                            # Target is model name or model path.
                            target_list.append(mapping)
                            break
                    else:
                        invalid_targets.append(target)

        if invalid_targets:
            raise Exception('The following targets were not recognized: %s' % invalid_targets)

        self.target_list = target_list or ModelMappings.mappings

    def index(self):
        """
        Do the actual indexing for all specified targets.
        """
        for mapping in self.target_list:
            model_name = mapping.get_mapping_type_name()
            main_index_base = settings.ES_INDEXES['default']
            main_index = get_index_name(main_index_base, mapping)

            self.stdout.write('==> %s' % model_name)

            # Check if we currently have an index for this mapping.
            old_index = None
            aliases = self.es.indices.get_aliases(name=main_index)
            for key, value in aliases.iteritems():
                if value['aliases']:
                    old_index = key
                    self.stdout.write('Current index "%s"' % key)

            # Check any indices with no alias (leftovers from failed indexing).
            # Or it could be that it is still in progress,
            aliases = self.es.indices.get_aliases()
            for key, value in aliases.iteritems():
                if not key.endswith(model_name):
                    # Not the model we are looking after.
                    continue
                if key == main_index:
                    # This is an auto created index. Will be removed at end of command.
                    continue
                if not value['aliases']:
                    if self.force:
                        self.stdout.write('Removing leftover "%s"' % key)
                        self.es.indices.delete(key)
                    else:
                        raise Exception(
                            'Found leftover %s, proceed with -f to remove.'
                            ' Make sure indexing this model is not already running!' % key
                        )

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
            self.es.indices.create(temp_index, body=index_settings)

            # Index documents.
            self.index_documents(mapping, temp_index_base)

            # Switch aliases.
            if old_index:
                self.es.indices.update_aliases({
                    'actions': [
                        {
                            'remove': {
                                'index': old_index,
                                'alias': main_index
                            }
                        },
                        {
                            'remove': {
                                'index': old_index,
                                'alias': main_index_base
                            }
                        },
                        {
                            'add': {
                                'index': temp_index,
                                'alias': main_index
                            }
                        },
                        {
                            'add': {
                                'index': temp_index,
                                'alias': main_index_base
                            }
                        },
                    ]
                })
                self.stdout.write('Removing previous index "%s"' % old_index)
                self.es.indices.delete(old_index)
            else:
                if self.es.indices.exists(main_index):
                    # This is a corner case. There was no alias named index_name, but
                    # an index index_name nevertheless exists, this only happens when the index
                    # was already created (because of ES auto creation features).
                    self.stdout.write('Removing previous (presumably auto created) index "%s"' % main_index)
                    self.es.indices.delete(main_index)
                self.es.indices.update_aliases({
                    'actions': [
                        {
                            'add': {
                                'index': temp_index,
                                'alias': main_index
                            }
                        },
                        {
                            'add': {
                                'index': temp_index,
                                'alias': main_index_base
                            }
                        },
                    ]
                })
            self.stdout.write('')

        self.stdout.write('Indexing finished.')

    def index_documents(self, mapping, temp_index_base):
        """
        Index all non deleted objects.
        """
        model = mapping.get_model()
        self.stdout.write('Indexing {0}.{1}'.format(model.__module__, model.__name__).lower())

        if mapping.has_deleted():
            model_objs = model.objects.filter(is_deleted=False)
        else:
            model_objs = model.objects.all()

        index_objects(mapping, model_objs, temp_index_base, print_progress=True)

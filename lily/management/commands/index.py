from optparse import make_option
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from elasticutils.contrib.django import get_es

from lily.search.analyzers import get_analyzers
from lily.search.indexing import index_objects, unindex_objects
from lily.search.scan_search import ModelMappings


class Command(BaseCommand):
    help = """Index current model instances into Elasticsearch. It does this by
creating a new index, then changing the alias to point to the new index.
(afterwards removing the old index).

It uses custom index implementation for fast and synchronous indexing.

There are basically two ways to use this command, the first to index all
configured mappings, which will create a new index, apply mappings and such:

    index

The second way is to target a specific model, in which no new index will be
created and no mappings will be applied. It only indexes the specific model:

    index -t Contact

or with fully qualified name:

    index -t lily.contacts.models.Contact

It is possible to specify multiple models, using comma separation.

Note: Mappings are only suported for models with 'is_deleted' properties.
If you add a mapping for a regular model, then some extra steps are needed
to make sure deletions are picked up (during this management command).
You can do this by comparing the list of PKs before and after."""

    option_list = BaseCommand.option_list + (
        make_option('-u', '--url',
                    action='store',
                    dest='url',
                    default='',
                    help='Override the ES_URLS in settings.',
                    ),
        make_option('-t', '--target',
                    action='store',
                    dest='target',
                    default='',
                    help='Choose specific model targets, comma separated.'
                    ),
        make_option('-i', '--id',
                    action='store',
                    dest='id',
                    default='',
                    help='Choose specific IDs, comma separated. Has no effect without "target" option.'
                    ),
        make_option('-q', '--queries',
                    action='store_true',
                    dest='queries',
                    help='Show the queries that were executed during the command.'
                    ),
    )

    def handle(self, *args, **options):
        url = options['url']
        if url:
            es = get_es(urls=[url])
        else:
            es = get_es()

        # Check if specific targets specified to run, or otherwise run all.
        target = options['target']
        if target:
            targets = target.split(',')
            # Check specific IDs.
            if options['id']:
                ids = options['id'].split(',')
                self.index(settings.ES_INDEXES['default'], specific_targets=targets, ids=ids, with_unindex=True)
            else:
                self.index(settings.ES_INDEXES['default'], specific_targets=targets, with_unindex=True)

        else:
            # We define some custom analyzers that our mappings can use.
            index_settings = {'mappings': {}, 'settings': get_analyzers()}

            # Retrieve the mappings for the index-enabled models.
            for mapping_class in ModelMappings.get_model_mappings().values():
                model_name = mapping_class.get_mapping_type_name()
                index_settings['mappings'].update({model_name: mapping_class.get_mapping()})

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
            # (In the sense that deletions are not picked up).
            self.index(index_name, with_unindex=True)

        if options['queries']:
            from django.db import connection
            for query in connection.queries:
                print query

    def index(self, index_name, specific_targets=None, ids=None, with_unindex=False):
        """
        Index objects from our index-enabled models.
        """
        for mapping_class in ModelMappings.get_model_mappings().values():
            model = mapping_class.get_model()
            # Skip this model if there are specific targets and not specified.
            if not self.model_targetted(model, specific_targets):
                continue
            model = mapping_class.get_model()
            self.stdout.write('%s: Indexing %s' % (index_name,
                                                   self.full_name(model)))

            if mapping_class.has_deleted():
                model_objs = model.objects.filter(is_deleted=False)
            else:
                model_objs = model.objects.all()

            if ids:
                model_objs = model_objs.filter(id__in=ids)

            index_objects(mapping_class, model_objs, index_name, print_progress=True)

            if with_unindex:
                if mapping_class.has_deleted():
                    model_objs = model.objects.filter(is_deleted=True)
                    if ids:
                        model_objs = model_objs.filter(id__in=ids)
                    unindex_objects(mapping_class, model_objs, index_name, print_progress=True)
                else:
                    # TODO: implement unindex for deleted items
                    pass

    def model_targetted(self, model, specific_targets):
        """
        Check if the model is targetted for indexing. If no specific targets
        are specified, all models are indexed.
        """
        if not specific_targets:
            return True
        for specific_target in specific_targets:
            if specific_target in [model.__name__, self.full_name(model)]:
                return True
        return False

    def full_name(self, model):
        """
        Get the fully qualified name of a model
        """
        return '%s.%s' % (model.__module__, model.__name__)

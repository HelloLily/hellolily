from __future__ import absolute_import, unicode_literals
import time

from django.utils.six.moves import input
from django.core.management import BaseCommand, CommandError
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl.connections import connections
from lily.settings.settings import ELASTICSEARCH_DSL


class Command(BaseCommand):
    possible_actions = ('create', 'autoalias', 'list', 'populate', 'delete', 'rebuild', 'cleanup', 'models', )

    def add_arguments(self, parser):
        parser.add_argument(
            '--models',
            metavar='app[.model]',
            type=str,
            nargs='*',
            help="Specify the model or app to be updated in elasticsearch"
        )
        parser.add_argument(
            'action',
            help='The subcommand to use',
        )
        parser.add_argument(
            '-f',
            action='store_true',
            dest='force',
            help="Force operations without asking"
        )
        parser.add_argument(
            '--using',
            default='default',
            help='Which Elasticsearch connection should be used (default: default)'
        )
        parser.add_argument(
            '--current',
            action='store_true',
            help='Populate models to the current index rather than the latest one.',
        )

    def handle(self, **options):
        """
        Entry point for the command.

        Args:
            options: The CLI arguments of the command.
        """
        action = options['action']
        models = self._get_models(options['models'])
        connections.configure(**ELASTICSEARCH_DSL)
        connection = connections.get_connection(options['using'])

        try:
            func = getattr(self, 'handle_{}'.format(action))
        except AttributeError:
            raise CommandError("Invalid action {}. Must be one of: {}".format(
                action, ', '.join(self.possible_actions),
            ))

        func(models, options, connection)

    def _get_models(self, args):
        """
        Get Models from registry that match the --models args.
        """
        if args:
            models = []
            for arg in args:
                arg = arg.lower()
                match_found = False

                for model in registry.get_models():
                    if model._meta.app_label == arg:
                        models.append(model)
                        match_found = True
                    elif model._meta.model_name.lower() == arg:
                        models.append(model)
                        match_found = True
                    elif '{}.{}'.format(model._meta.app_label.lower(), model._meta.model_name.lower()) == arg:
                        models.append(model)
                        match_found = True

                if not match_found:
                    raise CommandError("No model or app named {}".format(arg))
        else:
            models = registry.get_models()

        return set(models)

    def handle_create(self, models, options, connection):
        """
        Create new indices and point the aliases to them.

        Args:
            models: An iterable with model classes.
            options: A dict with command line options.
            connection: The Elasticsearch connection.
        """
        for index in registry.get_indices(models):
            index_name = '{}.{}'.format(index, int(time.time()))
            self.stdout.write("Creating index '{}'".format(index_name))
            connection.indices.create(index=index_name, body=index.to_dict())

    def handle_autoalias(self, models, options, connection):
        """
        Update the aliases to point to the latest index.

        Args:
            models: An iterable with model classes.
            options: A dict with command line options.
            connection: The Elasticsearch connection.
        """
        for index in registry.get_indices(models):
            indices = connection.indices.get('{}.*'.format(index))
            index_names = indices.keys()
            index_names.sort()
            last_index = index_names[-1]

            self.stdout.write("Pointing alias '{}' to '{}'".format(last_index, index))
            connection.indices.delete_alias(name=index, index='*', ignore=404)
            connection.indices.put_alias(index=last_index, name=index)

    def handle_list(self, models, options, connection):
        """
        List the current Elasticsearch indices.

        Args:
            models: The models to show the indices for.
            options: The command line options.
            connection: The Elasticsearch connection.
        """
        for index in registry.get_indices(models):
            indices = connection.indices.get('{}.*'.format(index))

            if indices:
                active_index = None
                for index_name, index_body in indices.items():
                    if str(index) in index_body.get('aliases', {}):
                        active_index = index_name
                        break

                self.stdout.write('Indices for \'{}\' (current {}): {}'.format(
                    index, active_index, ', '.join(indices.keys())
                ))
            else:
                self.stdout.write('No indices for \'{}\''.format(index))

    def handle_populate(self, models, options, connection):
        """
        Insert all given models in their respective indices.

        Args:
            models: An iterable with model classes.
            options: A dict with command line options.
            connection: The Elasticsearch connection.
        """
        for doc in registry.get_documents(models):
            qs = doc().get_queryset()

            if not options['current']:
                # We want to find and populate the latest index.
                indices = connection.indices.get('{}.*'.format(doc._doc_type.index)).keys()

                if not indices:
                    raise AttributeError('The index \'{}\' does not exist.'.format(doc._doc_type.index))

                indices.sort()
                doc._doc_type.index = indices[-1]  # Dirty hack to override the doctype meta, but it works.
            elif not connection.indices.exists(doc._doc_type.index):
                # We want to use the current index, which means we can use the
                # alias. If so, we do need to check the alias/index exists, or
                # we risk creating an index implicitly (which is a mess to
                # clean up).
                raise AttributeError('The index \'{}\' does not exist.'.format(doc._doc_type.index))

            self.stdout.write("Indexing {} '{}' objects to '{}'".format(
                qs.count(), doc._doc_type.model.__name__, doc._doc_type.index)
            )

            doc().update(qs)

    def handle_delete(self, models, options, connection):
        """
        Delete the current indices for the given models.

        Args:
            models: An iterable with model classes.
            options: The command line options.
            connection: The Elasticsearch connection.
        """
        index_names = [str(index) for index in registry.get_indices(models)]

        if not options['force']:
            response = input(
                "Are you sure you want to delete the '{}' indices? [n/Y]: ".format(", ".join(index_names))
            )
            if response.lower() != 'y':
                self.stdout.write('Aborted.')
                return False

        for index in registry.get_indices(models):
            self.stdout.write("Deleting index '{}'".format(index))
            connection.indices.delete('{}.*'.format(index), ignore=404)
            connection.indices.delete(str(index), ignore=404)

    def handle_rebuild(self, models, options, connection):
        """
        Rebuild Elasticsearch indices.

        Args:
            models: An iterable with model classes.
            options: The command line options.
            connection: The Elasticsearch connection.
        """
        index_names = [str(index) for index in registry.get_indices(models)]

        if options['current']:
            raise CommandError('Using the --current option is not supported with rebuild.')

        if not options['force']:
            answer = input("Are you sure you want to rebuild indices '{}'? [n/Y]: ".format(", ".join(index_names)))
            if answer.lower() != 'y':
                self.stdout.write('Aborted')
                return False

        self.handle_create(models, options, connection)
        self.handle_populate(models, options, connection)
        self.handle_list(models, options, connection)
        self.handle_autoalias(models, options, connection)
        self.handle_cleanup(models, options, connection)

    def handle_cleanup(self, models, options, connection):
        """
        Delete any inactive indices for the given models.

        Args:
            models: The models to show the indices for.
            options: The command line options.
            connection: The Elasticsearch connection.
        """
        for index in registry.get_indices(models):
            indices = connection.indices.get('{}.*'.format(index))

            if indices:
                old_indices = [name for name, body in indices.items() if str(index) not in body.get('aliases', {})]

                if old_indices:
                    self.stdout.write("Deleting old indices: {}".format(', '.join(old_indices)))
                    connection.indices.delete(index=','.join(old_indices))
                else:
                    self.stdout.write("No old indices found for {}".format(index))
            else:
                self.stdout.write('No indices for \'{}\''.format(index))

    def handle_models(self, models, options, connection):
        """
        List the possible model targets.

        Args:
            models: The models to show the indices for.
            options: The command line options.
            connection: The Elasticsearch connection.
        """
        selected = set()

        if options['models']:
            for model in models:
                selected.add('{}.{}'.format(model._meta.app_label, model.__name__))

            self.stdout.write('You have targeted these models:')
        else:
            for model in models:
                selected.add(model._meta.app_label)
                selected.add(model._meta.model_name)
                selected.add('{}.{}'.format(model._meta.app_label.lower(), model._meta.model_name))

            self.stdout.write('These models (case insensitive) are eligible for indexing:')

        for option in sorted(selected):
            self.stdout.write('- {}'.format(option))

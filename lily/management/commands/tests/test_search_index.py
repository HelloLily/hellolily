from unittest import TestCase

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import models
from django.utils.six import StringIO
from django_elasticsearch_dsl.documents import DocType
from django_elasticsearch_dsl.registries import DocumentRegistry
from mock import DEFAULT, Mock, patch, MagicMock

from lily.management.commands import search_index


class SearchIndexTestCase(TestCase):
    class ModelA(models.Model):
        class Meta:
            app_label = 'foo'

    class ModelB(models.Model):
        class Meta:
            app_label = 'foo'

    class ModelC(models.Model):
        class Meta:
            app_label = 'bar'

    class ModelD(models.Model):
        pass

    class ModelE(models.Model):
        pass

    def _generate_doc_mock(self, _model, index=None, mock_qs=None, _ignore_signals=False, _related_models=None):
        class Doc(DocType):
            class Meta:
                model = _model
                ignore_signals = _ignore_signals
                related_models = _related_models if _related_models is not None else []

        Doc.update = Mock()
        if mock_qs:
            Doc.get_queryset = Mock(return_value=mock_qs)
        if _related_models:
            Doc.get_instances_from_related = Mock()

        if index:
            Doc._doc_type.index = index
            self.registry.register(index, Doc)

        return Doc

    def setUp(self):
        self.out = StringIO()
        search_index.registry = self.registry = DocumentRegistry()
        self.index_a = Mock()
        self.index_a.__str__ = Mock(return_value='index_a')
        self.index_b = Mock()
        self.index_b.__str__ = Mock(return_value='index_b')

        self.doc_a1_qs = Mock()
        self.doc_a1 = self._generate_doc_mock(
            self.ModelA, self.index_a, self.doc_a1_qs
        )

        self.doc_a2_qs = Mock()
        self.doc_a2 = self._generate_doc_mock(
            self.ModelA, self.index_a, self.doc_a2_qs
        )

        self.doc_b1_qs = Mock()
        self.doc_b1 = self._generate_doc_mock(
            self.ModelB, self.index_a, self.doc_b1_qs
        )

        self.doc_c1_qs = Mock()
        self.doc_c1 = self._generate_doc_mock(
            self.ModelC, self.index_b, self.doc_c1_qs
        )

        self.patcher = patch('lily.management.commands.search_index.connections', MagicMock())
        connections = self.patcher.start()
        self.indices_client = connections.get_connection().indices

        def side_effect(value):
            if value.startswith('index_a'):
                return {'index_a.1': {'aliases': ['index_a']}, 'index_a.2': {}}
            else:
                return {'index_b.0': {}}

        self.indices_client.get.side_effect = side_effect

    def tearDown(self):
        self.patcher.stop()

    def test_get_models(self):
        """
        Test get_models() returns the models matching the app or name.
        """
        cmd = search_index.Command()

        self.assertEqual(cmd._get_models(['foo']), {self.ModelA, self.ModelB})
        self.assertEqual(cmd._get_models(['foo', 'bar.ModelC']), {self.ModelA, self.ModelB, self.ModelC})
        self.assertEqual(cmd._get_models([]), {self.ModelA, self.ModelB, self.ModelC})
        self.assertEqual(cmd._get_models(['modelc']), {self.ModelC})

        with self.assertRaises(CommandError):
            cmd._get_models(['unknown'])

    def test_no_action_error(self):
        """
        Test command raises error if no action is specified.
        """
        cmd = search_index.Command()
        with self.assertRaises(CommandError):
            cmd.handle(action='', models=[], using='default')

    def test_delete_foo_index(self):
        """
        Test delete deletes all matching indices.
        """
        search_index.input = Mock(return_value='y')

        call_command('search_index', 'delete', stdout=self.out, models=['foo'])
        self.assertEqual(2, self.indices_client.delete.call_count)
        self.indices_client.delete.assert_any_call('index_a.*', ignore=404)
        self.indices_client.delete.assert_any_call('index_a', ignore=404)
        self.index_a.delete.assert_not_called()
        self.index_b.delete.assert_not_called()

    def test_force_delete_all_indices(self):
        """
        Test delete skips verification with -f.
        """
        call_command('search_index', 'delete', stdout=self.out, force=True)

        self.assertEqual(4, self.indices_client.delete.call_count)
        self.indices_client.delete.assert_any_call('index_a.*', ignore=404)
        self.indices_client.delete.assert_any_call('index_a', ignore=404)
        self.indices_client.delete.assert_any_call('index_b.*', ignore=404)
        self.indices_client.delete.assert_any_call('index_b', ignore=404)
        self.index_a.delete.assert_not_called()
        self.index_b.delete.assert_not_called()

    def test_delete_abort(self):
        """
        Test delete can be aborted.
        """
        search_index.input = Mock(return_value='n')

        call_command('search_index', 'delete', stdout=self.out)

        self.index_a.delete.assert_not_called()
        self.index_b.delete.assert_not_called()
        self.indices_client.delete.assert_not_called()

    def test_create_all_indices(self):
        """
        Test create creates new indices.
        """
        call_command('search_index', 'create', stdout=self.out)

        self.index_a.create.assert_not_called()
        self.index_b.create.assert_not_called()

        indices = [call[1]['index'] for call in self.indices_client.create.call_args_list]
        self.assertEqual(2, len(indices))
        self.assertTrue(indices[1].startswith('index_b.' if indices[0].startswith('index_a.') else 'index_a.'))

    def test_populate_all_doc_type(self):
        """
        Test populate inserts models in index.
        """
        self.indices_client.exists.return_value = True

        call_command('search_index', 'populate', stdout=self.out)

        self.doc_a1.get_queryset.assert_called_once()
        self.doc_a1.update.assert_called_once_with(self.doc_a1_qs)
        self.doc_a2.get_queryset.assert_called_once()
        self.doc_a2.update.assert_called_once_with(self.doc_a2_qs)
        self.doc_b1.get_queryset.assert_called_once()
        self.doc_b1.update.assert_called_once_with(self.doc_b1_qs)
        self.doc_c1.get_queryset.assert_called_once()
        self.doc_c1.update.assert_called_once_with(self.doc_c1_qs)

    def test_populate_index_does_not_exist(self):
        """
        Test populate raises an error if the index does not exist.
        """
        self.indices_client.exists.return_value = False
        self.indices_client.get.side_effect = None
        self.indices_client.get.return_value = {}

        with self.assertRaises(AttributeError):
            call_command('search_index', 'populate', stdout=self.out)

        self.doc_a1.update.assert_not_called()
        self.doc_a2.update.assert_not_called()
        self.doc_b1.update.assert_not_called()
        self.doc_c1.update.assert_not_called()

    def test_populate_current(self):
        """
        Test populate --current populates the currently active index.
        """
        call_command('search_index', 'populate', stdout=self.out, current=True)

        self.indices_client.exists.assert_any_call(self.doc_a1._doc_type.index)
        self.indices_client.exists.assert_any_call(self.doc_a2._doc_type.index)
        self.indices_client.exists.assert_any_call(self.doc_b1._doc_type.index)
        self.indices_client.exists.assert_any_call(self.doc_c1._doc_type.index)

    def test_populate_current_not_exists(self):
        """
        Test populate --current raises an error if the index does not exist.
        """
        self.indices_client.exists.return_value = False

        with self.assertRaises(AttributeError):
            call_command('search_index', 'populate', stdout=self.out, current=True)

    def test_autoalias(self):
        """
        Test autoalias points aliases to the latest indices.
        """
        call_command('search_index', 'autoalias', stdout=self.out)

        self.indices_client.delete_alias.assert_any_call(name=self.index_a, index='*', ignore=404)
        self.indices_client.delete_alias.assert_any_call(name=self.index_b, index='*', ignore=404)
        self.indices_client.put_alias.assert_any_call(index='index_a.2', name=self.index_a)
        self.indices_client.put_alias.assert_any_call(index='index_b.0', name=self.index_b)

    def test_list(self):
        """
        Test list lists the indices for an alias.
        """
        call_command('search_index', 'list', stdout=self.out)

        lines = [line for line in self.out.getvalue().split('\n') if line]
        self.assertEqual(2, len(lines))
        self.assertTrue("Indices for 'index_a' (current index_a.1): index_a.2, index_a.1" in lines)
        self.assertTrue("Indices for 'index_b' (current None): index_b.0" in lines)

    def test_list_no_indices(self):
        """
        Test list when there are no indices for an alias.
        """
        self.indices_client.get.side_effect = None
        self.indices_client.get.return_value = {}

        call_command('search_index', 'list', stdout=self.out, models=['bar'])

        self.assertEqual("No indices for 'index_b'\n", self.out.getvalue())

    def test_models(self):
        """
        Test models shows a list of eligible targets.
        """
        call_command('search_index', 'models', stdout=self.out)

        self.assertEqual('{}\n'.format('\n'.join([
            'These models (case insensitive) are eligible for indexing:',
            '- bar',
            '- bar.modelc',
            '- foo',
            '- foo.modela',
            '- foo.modelb',
            '- modela',
            '- modelb',
            '- modelc',
        ])), self.out.getvalue())

    def test_models_with_models(self):
        """
        Test models shows a list of selected targets.
        """
        call_command('search_index', 'models', stdout=self.out, models=['foo'])

        self.assertEqual('{}\n'.format('\n'.join([
            'You have targeted these models:',
            '- foo.ModelA',
            '- foo.ModelB',
        ])), self.out.getvalue())

    def test_cleanup(self):
        """
        Test cleanup removes unused indices.
        """
        call_command('search_index', 'cleanup', stdout=self.out)

        self.assertEqual(2, self.indices_client.get.call_count)
        self.indices_client.get.assert_any_call('index_a.*')
        self.indices_client.get.assert_any_call('index_b.*')

        self.assertEqual(2, self.indices_client.delete.call_count)
        self.indices_client.delete.assert_any_call(index='index_a.2')
        self.indices_client.delete.assert_any_call(index='index_b.0')

    def test_cleanup_no_old_indices(self):
        """
        Test cleanup doesn't remove if all indices are in use.
        """
        def side_effect(value):
            if value.startswith('index_a'):
                return {'index_a.1': {'aliases': ['index_a']}, 'index_a.2': {}}
            else:
                return {'index_b.0': {'aliases': ['index_b']}}

        self.indices_client.get.side_effect = side_effect

        call_command('search_index', 'cleanup', stdout=self.out)

        self.assertEqual(1, self.indices_client.delete.call_count)
        self.indices_client.delete.assert_called_with(index='index_a.2')

    def test_cleanup_no_indices(self):
        """
        Test cleanup without any indices.
        """
        self.indices_client.get.return_value = {}
        self.indices_client.delete.assert_not_called()

    def test_rebuild(self):
        """
        Test rebuild calls the appropriate methods.
        """
        with patch.multiple(
                search_index.Command, handle_create=DEFAULT, handle_populate=DEFAULT, handle_autoalias=DEFAULT,
                handle_cleanup=DEFAULT
        ) as handles:
            search_index.input = Mock(return_value='y')

            call_command('search_index', 'rebuild', stdout=self.out)

            handles['handle_create'].assert_called()
            handles['handle_populate'].assert_called()
            handles['handle_autoalias'].assert_called()
            handles['handle_cleanup'].assert_called()

    def test_rebuild_aborted(self):
        """
        Test rebuild is aborted.
        """
        with patch.multiple(
                search_index.Command, handle_create=DEFAULT, handle_populate=DEFAULT, handle_autoalias=DEFAULT,
                handle_cleanup=DEFAULT
        ) as handles:
            search_index.input = Mock(return_value='n')

            call_command('search_index', 'rebuild', stdout=self.out)

            handles['handle_create'].assert_not_called()
            handles['handle_populate'].assert_not_called()
            handles['handle_autoalias'].assert_not_called()
            handles['handle_cleanup'].assert_not_called()

    def test_rebuild_current(self):
        """
        Test rebuild rejects --current.
        """
        with patch.multiple(
                search_index.Command, handle_create=DEFAULT, handle_populate=DEFAULT, handle_autoalias=DEFAULT,
                handle_cleanup=DEFAULT
        ) as handles:
            search_index.input = Mock(return_value='y')

            with self.assertRaises(CommandError):
                call_command('search_index', 'rebuild', stdout=self.out, current=True)

            handles['handle_create'].assert_not_called()
            handles['handle_populate'].assert_not_called()
            handles['handle_autoalias'].assert_not_called()
            handles['handle_cleanup'].assert_not_called()

    def test_rebuild_force(self):
        """
        Test rebuild accepts -f.
        """
        with patch.multiple(
                search_index.Command, handle_create=DEFAULT, handle_populate=DEFAULT, handle_autoalias=DEFAULT,
                handle_cleanup=DEFAULT
        ) as handles:
            search_index.input = Mock(return_value='CRASH!')

            call_command('search_index', 'rebuild', stdout=self.out, force=True)

            handles['handle_create'].assert_called()
            handles['handle_populate'].assert_called()
            handles['handle_autoalias'].assert_called()
            handles['handle_cleanup'].assert_called()

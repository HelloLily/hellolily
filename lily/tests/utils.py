from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from urllib import urlencode

from django.contrib.auth.models import AnonymousUser, Group
from django.db.models import Manager, Model
from django_elasticsearch_dsl import Index
from django_elasticsearch_dsl.registries import registry
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import OAuth2Credentials
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from lily.tenant.factories import TenantFactory
from lily.tenant.middleware import set_current_user
from lily.users.models import LilyUser, UserInfo


class UserBasedTest(object):
    """
    Baseclass that provides functionality for tests that require a logged in user.
    """
    factory_cls = None

    @classmethod
    def setUpTestData(cls):
        """
        Creates a user and logs it in before running the actual tests.
        """
        password = 'password'
        set_current_user(None)

        # Set the anonymous user on the class.
        cls.anonymous_user_obj = AnonymousUser()
        cls.anonymous_user = APIClient()

        tenant_1 = TenantFactory.create()
        tenant_2 = TenantFactory.create()

        # Set the authenticated user on the class.
        cls.user_obj = LilyUser.objects.create_user(
            email='user1@lily.com',
            password=password,
            tenant_id=tenant_1.id
        )

        account_admin = Group.objects.get_or_create(name='account_admin')[0]
        cls.user_obj.groups.add(account_admin)

        cls.user_obj.info = UserInfo.objects.create(
            registration_finished=True
        )
        cls.user_obj.save()

        cls.user = APIClient()
        cls.user.login(username=cls.user_obj.email, password=password)

        # Set the superuser on the class.
        cls.superuser_obj = LilyUser.objects.create_superuser(
            email='superuser1@lily.com',
            password=password,
            tenant_id=tenant_1.id
        )
        cls.superuser_obj.info = UserInfo.objects.create(
            registration_finished=True
        )
        cls.superuser_obj.save()

        cls.superuser = APIClient()
        cls.superuser.login(username=cls.superuser_obj.email, password=password)

        # Set the authenticated user from another tenant on the class.
        cls.other_tenant_user_obj = LilyUser.objects.create_user(
            email='user2@lily.com',
            password=password,
            tenant_id=tenant_2.id
        )
        cls.other_tenant_user_obj.info = UserInfo.objects.create(
            registration_finished=True
        )
        cls.other_tenant_user_obj.save()

        cls.other_tenant_user = APIClient()
        cls.other_tenant_user.login(username=cls.other_tenant_user_obj.email, password=password)

    @classmethod
    def tearDownClass(cls):
        set_current_user(None)
        super(UserBasedTest, cls).tearDownClass()

    def _create_object(self, with_relations=False, size=1, **kwargs):
        """
        Default implentation for the creation of objects, this doesn't do anything with relations other than
        what the factory does by default..
        """
        # Set a default tenant of the user.
        kwargs['tenant'] = self.user_obj.tenant if not kwargs.get('tenant') else kwargs['tenant']

        object_list = self.factory_cls.create_batch(size=size, **kwargs)

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def _create_object_stub(self, with_relations=False, size=1, force_to_list=False, **kwargs):
        """
        Default implentation for the creation of stubs, this doesn't do anything with relations other than
        what the factory does by default.
        """
        # Set a default tenant of the user.
        kwargs['tenant'] = None

        object_list = self.factory_cls.stub_batch(size=size, **kwargs)

        return self._formatted_stub(object_list, size, force_to_list)

    def _formatted_stub(self, object_list, size, force_to_list=False):
        """ Returns the object or a list of object(s) depending on size and
        force_to_list. """
        if size > 1 or force_to_list:
            return [obj.__dict__ for obj in object_list]

        # If required size is 1 and force_to_list is False, just give the object instead of a list.
        return object_list[0].__dict__


class CompareObjectsMixin(object):
    """
    Baseclass that provides functionality for tests that compare objects.
    """

    def assertStatus(self, request, desired_code, original_data=None):
        """
        Helper function to assert that the response of the API is what is expected.
        If the response status code doesn't match log the response for debugging.
        """
        if request.status_code != desired_code:
            print('')
            print('%s.%s' % (self.model_cls.__name__, self._testMethodName))
            print(request.data)
            print('')
            if original_data:
                for key in request.data:
                    print('original data:')
                    print(original_data.get(key, 'Original data not available for %s' % key))
            print('')

        self.assertEqual(request.status_code, desired_code)

    def _transform_value(self, value):
        """
        Transform the value into something comparable.

        Date: transform to string like so: 2015-11-23
        Datetime: transform into string like so: 2015-11-23T10:58:31.754643Z

        If value is not a date/datetime do nothing and return.
        """
        if isinstance(value, datetime):
            # In the case of datetime special formatting is required.
            db_value = value.isoformat()
            if db_value.endswith('+00:00'):
                value = db_value[:-6] + 'Z'

        if isinstance(value, Decimal):
            value = str(value)

        if isinstance(value, date):
            value = value.isoformat()

        return value

    def _compare_objects(self, db_obj, api_obj, serializer=None):
        """
        Compare two objects with each other based on the fields of the API serializer.
        """
        serializer = serializer if serializer else self.serializer_cls
        serializer_field_list = serializer.Meta.fields
        model_field_list = [f.name for f in self.model_cls._meta.get_fields()]

        for field in serializer_field_list:
            if field in model_field_list and not field:
                # Make sure the field is in the response.
                self.assertIn(field, api_obj)

                db_value = getattr(db_obj, field)
                api_value = api_obj.get(field)

                db_value = self._transform_value(db_value)

                if isinstance(db_value, Model) or isinstance(db_value, Manager):
                    # Relationships can't be checked generically
                    continue

                # Make sure the field value matches that of the factory object.
                self.assertEqual(api_value, db_value)


class GenericAPITestCase(CompareObjectsMixin, UserBasedTest, APITestCase):
    list_url = None
    detail_url = None
    factory_cls = None
    model_cls = None
    serializer_cls = None
    ordering = ('-id',)  # Default ordering field
    es_doc_type = None

    @classmethod
    def setUpTestData(cls):
        super(GenericAPITestCase, cls).setUpTestData()

        # Check if this model has Elasticsearch mappings and take one of them
        # to test with (unless a custom es_doc_type has been defined).
        if not cls.es_doc_type:
            doc_types = registry.get_documents(cls.model_cls)
            if doc_types:
                cls.es_doc_type = next(iter(doc_types))

    @classmethod
    def tearDownClass(cls):
        # Reset the es_doc_type class field for other tests.
        cls.es_doc_type = None

        super(GenericAPITestCase, cls).tearDownClass()

    def __call__(self, result=None):
        """
        Skip the GenericAPITestCase base class tests that nose mistakenly
        finds.

        Args:
            nose_testresult (TextTestResult): A nose TextTestResult instance.
        """
        if 'GenericAPITestCase' not in str(type(self)):
            return super(GenericAPITestCase, self).__call__(result)

    def get_url(self, name, ordering=None, action_name='', *args, **kwargs):
        base_url = reverse(name, *args, **kwargs)

        if action_name != '':
            action_name += '/'

        query_params = urlencode({'ordering': ordering or ','.join(self.ordering)})

        return '{}{}?{}'.format(base_url, action_name, query_params)

    def test_get_list_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have access to the list.
        """
        request = self.anonymous_user.get(self.get_url(self.list_url))
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_get_list_authenticated(self):
        """
        Test that the list returns normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        obj_list = self._create_object(size=3)

        request = self.user.get(self.get_url(self.list_url))

        self.assertStatus(request, status.HTTP_200_OK)
        self.assertEqual(len(obj_list), len(request.data.get('results')))

        for i, db_obj in enumerate(reversed(obj_list)):
            api_obj = request.data.get('results')[i]
            self._compare_objects(db_obj, api_obj)

    def test_get_list_deleted_filter(self):
        """
        Test that deleted objects are not returned as part of the list.
        """
        set_current_user(self.user_obj)
        obj_list = self._create_object(size=3)

        obj_to_delete = obj_list.pop()
        obj_to_delete.delete()

        request = self.user.get(self.get_url(self.list_url))

        self.assertStatus(request, status.HTTP_200_OK)
        self.assertEqual(len(obj_list), len(request.data.get('results')))

        for i, db_obj in enumerate(reversed(obj_list)):
            self._compare_objects(db_obj, request.data.get('results')[i])

    def test_get_list_tenant_filter(self):
        """
        Test that users from different tenants can't access each other's data.
        """
        set_current_user(self.other_tenant_user_obj)
        other_tenant_obj_list = self._create_object(size=3, tenant=self.other_tenant_user_obj.tenant)

        set_current_user(self.user_obj)
        self._create_object(size=3)

        request = self.other_tenant_user.get(self.get_url(self.list_url))
        self.assertStatus(request, status.HTTP_200_OK)
        self.assertEqual(len(other_tenant_obj_list), len(request.data.get('results')))

        for i, db_obj in enumerate(reversed(other_tenant_obj_list)):
            self._compare_objects(db_obj, request.data.get('results')[i])

    def test_get_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have access to the object.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        request = self.anonymous_user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_get_object_authenticated(self):
        """
        Test that the object returns normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        request = self.user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_200_OK)
        self._compare_objects(db_obj, json.loads(request.content))

    def test_get_object_deleted_filter(self):
        """
        Test that deleted objects are not returned.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()
        db_obj.delete()  # Delete the object

        request = self.user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_get_object_tenant_filter(self):
        """
        Test that users from different tenants can't access each other's data.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        request = self.other_tenant_user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_create_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to create an object.
        """
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub()

        request = self.anonymous_user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_403_FORBIDDEN, stub_dict)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_create_object_authenticated(self):
        """
        Test that the object is created normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub()

        request = self.user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_201_CREATED, stub_dict)

        created_id = json.loads(request.content).get('id')
        self.assertIsNotNone(created_id)

        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, json.loads(request.content))

        if self.es_doc_type:
            Index(self.es_doc_type._doc_type.index).refresh()
            self.assertIsNotNone(self.es_doc_type.get(id=db_obj.pk))

    def test_create_object_tenant_filter(self):
        """
        Test that the tenant is set correctly on the new object.
        """
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub()

        request = self.user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_201_CREATED, stub_dict)

        db_obj = self.model_cls.objects.get(pk=request.data.get('id'))
        self.assertEqual(self.user_obj.tenant, db_obj.tenant)

    def test_update_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to update an object.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()
        stub_dict = self._create_object_stub()

        request = self.anonymous_user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), stub_dict)
        self.assertStatus(request, status.HTTP_403_FORBIDDEN, stub_dict)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_update_object_authenticated(self):
        """
        Test that the object is updated normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()
        stub_dict = self._create_object_stub()

        if self.es_doc_type:
            Index(self.es_doc_type._doc_type.index).refresh()
            old_es_doc = self.es_doc_type.get(id=db_obj.pk)

        request = self.user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), data=stub_dict)
        self.assertStatus(request, status.HTTP_200_OK, stub_dict)

        created_id = request.data.get('id')
        self.assertIsNotNone(created_id)

        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, request.data)

        if self.es_doc_type:
            Index(self.es_doc_type._doc_type.index).refresh()
            updated_es_doc = self.es_doc_type.get(id=created_id)

            self.assertNotEqual(old_es_doc.to_dict(), updated_es_doc.to_dict())

    def test_update_object_deleted_filter(self):
        """
        Test that deleted objects can't be updated.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()
        db_obj.delete()  # Delete the object

        stub_dict = self._create_object_stub()

        request = self.user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), data=stub_dict)
        self.assertStatus(request, status.HTTP_404_NOT_FOUND, stub_dict)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_update_object_tenant_filter(self):
        """
        Test that users from different tenants can't update each other's data.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()
        stub_dict = self._create_object_stub()

        if self.es_doc_type:
            Index(self.es_doc_type._doc_type.index).refresh()
            old_es_doc = self.es_doc_type.get(id=db_obj.pk)

        request = self.other_tenant_user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), stub_dict)
        self.assertStatus(request, status.HTTP_404_NOT_FOUND, stub_dict)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

        if self.es_doc_type:
            Index(self.es_doc_type._doc_type.index).refresh()
            updated_es_doc = self.es_doc_type.get(id=db_obj.pk)

            self.assertEqual(old_es_doc.to_dict(), updated_es_doc.to_dict())

    def test_delete_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to delete an object.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        request = self.anonymous_user.delete(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_delete_object_authenticated(self):
        """
        Test that the object is deleted normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        request = self.user.delete(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_204_NO_CONTENT)

        if 'is_deleted' in [f.name for f in self.model_cls._meta.get_fields()]:
            self.assertTrue(self.model_cls.objects.get(pk=db_obj.pk).is_deleted)

            if self.es_doc_type:
                Index(self.es_doc_type._doc_type.index).refresh()
                self.assertIsNotNone(self.es_doc_type.get(id=db_obj.pk))
        else:
            with self.assertRaises(self.model_cls.DoesNotExist):
                self.model_cls.objects.get(pk=db_obj.pk)

            if self.es_doc_type:
                Index(self.es_doc_type._doc_type.index).refresh()
                self.assertIsNotNone(self.es_doc_type.get(id=db_obj.pk))

    def test_delete_object_deleted_filter(self):
        set_current_user(self.user_obj)
        db_obj = self._create_object()
        db_obj.delete()  # Delete the object

        request = self.user.delete(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_delete_object_tenant_filter(self):
        """
        Test that users from different tenants can't delete each other's data.
        """
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        request = self.other_tenant_user.delete(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})


def get_url_with_query(name, params={}, *args, **kwargs):
    return '%s?%s' % (reverse(name, *args, **kwargs), urlencode(params))


class ElasticSearchFilterAPITest(object):
    search_attribute = None
    filter_field = None

    def test_list_search_with_elasticsearch(self):
        """
        Test list can be searched (with Elasticsearch).
        """
        set_current_user(self.user_obj)
        obj_list = self._create_object(size=3)

        for idx in registry.get_indices([self.model_cls]):
            idx.refresh()

        request = self.user.get(get_url_with_query(self.list_url), {
            'search': getattr(obj_list[0], self.search_attribute),
        })
        self.assertStatus(request, status.HTTP_200_OK)
        self._compare_objects(obj_list[0], request.data.get('results')[0])


def get_dummy_credentials():
    access_token = 'foo'
    client_id = 'some_client_id'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.utcnow() + timedelta(minutes=10)
    user_agent = 'refresh_checker/1.0'

    return OAuth2Credentials(
        access_token,
        client_id,
        client_secret,
        refresh_token,
        token_expiry,
        GOOGLE_TOKEN_URI,
        user_agent
    )

from datetime import datetime
import json
from unittest import SkipTest

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ForeignKey, Manager
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.utils import model_meta

from lily.tenant.middleware import set_current_user
from lily.tenant.models import Tenant
from lily.users.models import LilyUser


class UserBasedTest(object):
    """
    Baseclass that provides functionality for tests that require a logged in user.
    """
    @classmethod
    def setUpClass(cls):
        """
        Creates a user and logs it in before running the actual tests.
        """
        password = 'password'
        set_current_user(None)

        # Set the anonymous user on the class
        cls.anonymous_user_obj = AnonymousUser()
        cls.anonymous_user = APIClient()

        # Set the authenticated user on the class
        cls.user_obj = LilyUser.objects.create_user(email='user1@lily.com', password=password, tenant_id=1)
        cls.user = APIClient()
        cls.user.login(email=cls.user_obj.email, password=password)

        # Set the superuser on the class
        cls.superuser_obj = LilyUser.objects.create_superuser(email='superuser1@lily.com', password=password, tenant_id=1)
        cls.superuser = APIClient()
        cls.superuser.login(email=cls.superuser_obj.email, password=password)

        # Set the authenticated user from another tenant on the class
        cls.other_tenant_user_obj = LilyUser.objects.create_user(email='user2@lily.com', password=password, tenant_id=2)
        cls.other_tenant_user = APIClient()
        cls.other_tenant_user.login(email=cls.other_tenant_user_obj.email, password=password)

    @classmethod
    def tearDownClass(cls):
        """
        Remove the users after the tests
        """
        set_current_user(None)
        LilyUser.objects.all().delete()
        Tenant.objects.all().delete()


class GenericAPITestCase(UserBasedTest, APITestCase):
    list_url = None
    detail_url = None
    factory_cls = None
    model_cls = None
    serializer_cls = None

    def setUp(self):
        """
        Skip these tests if they are not run as a mixin.

        For some reason the testrunner recognizes these tests outside of a tests.py as well.
        But we don't want to run these if there is no serializer/model set.
        """
        if not self.model_cls or not self.serializer_cls:
            raise SkipTest

    def _compare_objects(self, db_obj, api_obj, serializer=None):
        """
        Compare two objects with eachother based on the fields of the API serializer.
        """
        serializer = serializer if serializer else self.serializer_cls()
        serializer_field_list = serializer.get_field_names(serializer._declared_fields, model_meta.get_field_info(self.model_cls))
        model_field_list = self.model_cls._meta.get_all_field_names()

        for field in serializer_field_list:
            if field in model_field_list:
                # Make sure the field is in the response
                self.assertIn(field, api_obj)

                db_value = getattr(db_obj, field)
                api_value = api_obj.get(field)

                if isinstance(db_value, datetime):
                    # In the case of datetime special formatting is required.
                    db_value = db_value.isoformat()
                    if db_value.endswith('+00:00'):
                        db_value = db_value[:-6] + 'Z'

                if isinstance(db_value, ForeignKey) or isinstance(db_value, Manager):
                    # Relationships can't be checked generically
                    continue

                # Make sure the field value matches that of the factory object
                self.assertEqual(api_value, db_value)

    def test_get_list_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have access to the list.
        """
        request = self.anonymous_user.get(reverse(self.list_url), format='json')
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_get_list_authenticated(self):
        """
        Test that the list returns normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        obj_list = self.factory_cls.create_batch(size=3, tenant=self.user_obj.tenant)

        request = self.user.get(reverse(self.list_url), format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        request_data = json.loads(request.content)
        self.assertEqual(len(obj_list), len(request_data))

        for i, db_obj in enumerate(reversed(obj_list)):
            api_obj = request_data[i]
            self._compare_objects(db_obj, api_obj)

    def test_get_list_deleted_filter(self):
        """
        Test that deleted objects are not returned as part of the list.
        """
        set_current_user(self.user_obj)
        obj_list = self.factory_cls.create_batch(size=3, tenant=self.user_obj.tenant)

        obj_to_delete = obj_list.pop()
        obj_to_delete.delete()
        request = self.user.get(reverse(self.list_url), format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        request_data = json.loads(request.content)
        self.assertEqual(len(obj_list), len(request_data))

        for i, db_obj in enumerate(reversed(obj_list)):
            api_obj = request_data[i]
            self._compare_objects(db_obj, api_obj)

    def test_get_list_tenant_filter(self):
        """
        Test that users from different tenants can't access eachothers data.
        """
        set_current_user(self.user_obj)
        self.factory_cls.create_batch(size=3, tenant=self.user_obj.tenant)
        other_tenant_obj_list = self.factory_cls.create_batch(size=3, tenant=self.other_tenant_user_obj.tenant)

        request = self.other_tenant_user.get(reverse(self.list_url), format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        request_data = json.loads(request.content)
        self.assertEqual(len(other_tenant_obj_list), len(request_data))

        for i, db_obj in enumerate(reversed(other_tenant_obj_list)):
            api_obj = request_data[i]
            self._compare_objects(db_obj, api_obj)

    def test_get_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have access to the object.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)

        request = self.anonymous_user.get(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_get_object_authenticated(self):
        """
        Test that the object returns normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)

        request = self.user.get(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self._compare_objects(db_obj, json.loads(request.content))

    def test_get_object_deleted_filter(self):
        """
        Test that deleted objects are not returned.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)
        db_obj.delete()  # Delete the object

        request = self.user.get(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_get_object_tenant_filter(self):
        """
        Test that users from different tenants can't access eachothers data.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)

        request = self.other_tenant_user.get(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_create_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to create an object.
        """
        set_current_user(self.user_obj)
        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.anonymous_user.post(reverse(self.list_url), stub_dict)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_create_object_authenticated(self):
        """
        Test that the object is created normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.user.post(reverse(self.list_url), stub_dict)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        created_id = json.loads(request.content).get('id')
        self.assertIsNotNone(created_id)

        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, json.loads(request.content))

    def test_create_object_tenant_filter(self):
        """
        Test that the tenant is set correctly on the new object.
        """
        set_current_user(self.user_obj)
        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.user.post(reverse(self.list_url), stub_dict)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        db_obj = self.model_cls.objects.get(pk=request.data.get('id'))
        self.assertEqual(self.user_obj.tenant, db_obj.tenant)

    def test_update_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to update an object.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)
        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.anonymous_user.put(reverse(self.detail_url, kwargs={'pk': db_obj.pk}), stub_dict)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_update_object_authenticated(self):
        """
        Test that the object is updated normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)
        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.user.put(reverse(self.detail_url, kwargs={'pk': db_obj.pk}), data=stub_dict)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        response = json.loads(request.content)

        for field_name, field_value in stub_dict.items():
            self.assertEqual(field_value, response.get(field_name))

    def test_update_object_deleted_filter(self):
        """
        Test that deleted objects can't be updated.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)
        db_obj.delete()  # Delete the object

        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.user.put(reverse(self.detail_url, kwargs={'pk': db_obj.pk}), data=stub_dict)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_update_object_tenant_filter(self):
        """
        Test that users from different tenants can't update eachothers data.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)
        stub_dict = self.factory_cls.stub().__dict__
        del stub_dict['tenant']

        request = self.other_tenant_user.put(reverse(self.detail_url, kwargs={'pk': db_obj.pk}), stub_dict)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_delete_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to delete an object.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)

        request = self.anonymous_user.delete(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_delete_object_authenticated(self):
        """
        Test that the object is deleted normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)

        request = self.user.delete(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

        if 'is_deleted' in self.model_cls._meta.get_all_field_names():
            self.assertTrue(self.model_cls.objects.get(pk=db_obj.pk).is_deleted)
        else:
            self.assertRaises(ObjectDoesNotExist, self.model_cls.objects.get(pk=db_obj.pk))

    def test_delete_object_deleted_filter(self):
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)
        db_obj.delete()  # Delete the object

        request = self.user.delete(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_delete_object_tenant_filter(self):
        """
        Test that users from different tenants can't delete eachothers data.
        """
        set_current_user(self.user_obj)
        db_obj = self.factory_cls.create(tenant=self.user_obj.tenant)

        request = self.other_tenant_user.delete(reverse(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

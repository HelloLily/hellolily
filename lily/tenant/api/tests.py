from urllib import urlencode

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from lily.tenant.api.serializers import TenantSerializer
from lily.tenant.factories import TenantFactory
from lily.tenant.middleware import set_current_user
from lily.tenant.models import Tenant
from lily.tests.utils import UserBasedTest, CompareObjectsMixin
from lily.utils.models.factories import ExternalAppLinkFactory


class TenantTests(CompareObjectsMixin, UserBasedTest, APITestCase):
    """
    Class containing tests for the tenant API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'tenant-list'
    detail_url = 'tenant-detail'
    factory_cls = TenantFactory
    model_cls = Tenant
    serializer_cls = TenantSerializer
    ordering = ('-id', )  # Default ordering field

    @classmethod
    def setUpTestData(cls):
        super(TenantTests, cls).setUpTestData()

        cls.user_obj.tenant.name = "User Tenant"
        cls.user_obj.tenant.save()
        ExternalAppLinkFactory.create(tenant_id=cls.user_obj.tenant_id)

        cls.other_tenant_user_obj.tenant.name = "Other Tenant User Tenant"
        cls.other_tenant_user_obj.tenant.save()
        ExternalAppLinkFactory.create(tenant_id=cls.other_tenant_user_obj.tenant_id)

    def get_url(self, name, ordering=None, *args, **kwargs):
        return '%s?%s' % (reverse(name, *args, **kwargs), urlencode({'ordering': ordering or ','.join(self.ordering)}))

    def _create_object_stub(self, size=1, **kwargs):
        """
        Create an object dict with relation dicts using factories.
        """
        object_list = []
        app_link_kwargs = kwargs
        app_link_kwargs['tenant_id'] = self.user_obj.tenant.pk
        for iteration in range(0, size):
            obj = self.factory_cls.stub(**kwargs).__dict__

            obj['external_app_links'] = ExternalAppLinkFactory.stub(**app_link_kwargs).__dict__
            del obj['billing']

            object_list.append(obj)

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def test_get_list_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have access to the tenants list.
        """
        request = self.anonymous_user.get(self.get_url(self.list_url))
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_get_list_authenticated(self):
        """
        Test that the list returns normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        request = self.user.get(self.get_url(self.list_url))

        self.assertStatus(request, status.HTTP_200_OK)
        self.assertEqual(1, len(request.data))

        db_obj = self.user_obj.tenant
        api_obj = request.data[0]
        self._compare_objects(db_obj, api_obj)

        for link in api_obj.get('external_app_links'):
            self.assertEquals(self.user_obj.tenant.pk, link.get('tenant_id'))

    def test_create_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to create a tenant.
        """
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub()

        request = self.anonymous_user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_create_object_authenticated(self):
        """
        Test that an authenticated user doesn't have the access to create a tenant.
        """
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub()

        request = self.user.post(self.get_url(self.list_url), stub_dict)

        self.assertStatus(request, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(request.data, {u'detail': u'Method "POST" not allowed.'})

    def test_update_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have the access to update a tenant.
        """
        set_current_user(self.user_obj)

        db_obj = self.user_obj.tenant
        stub_dict = self._create_object_stub()

        request = self.anonymous_user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), stub_dict)
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_update_object_authenticated_own(self):
        """
        Test that the tenant is updated normally when the user is properly authenticated.
        """
        set_current_user(self.user_obj)
        db_obj = self.user_obj.tenant
        stub_dict = self._create_object_stub()

        request = self.user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), data=stub_dict)
        self.assertStatus(request, status.HTTP_200_OK)

        updated_id = request.data.get('id')
        self.assertIsNotNone(updated_id)

        db_obj = self.model_cls.objects.get(pk=updated_id)
        self._compare_objects(db_obj, request.data)

    def test_update_object_authenticated_other(self):
        """
        Test that an authenticated user is not able to updated an other tenant.
        """
        set_current_user(self.user_obj)
        db_obj = self.other_tenant_user_obj.tenant
        stub_dict = self._create_object_stub()

        request = self.user.put(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}), data=stub_dict)
        self.assertStatus(request, status.HTTP_404_NOT_FOUND)
        self.assertEqual(request.data, {u'detail': u'Not found.'})

    def test_get_object_unauthenticated(self):
        """
        Test that an unauthenticated user doesn't have access to the tenant.
        """
        set_current_user(self.user_obj)
        db_obj = self.user_obj.tenant

        request = self.anonymous_user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request.data, {u'detail': u'Authentication credentials were not provided.'})

    def test_get_object_authenticated_own(self):
        """
        Test that an authenticated user doesn't have access to their own tenant details.
        """
        set_current_user(self.user_obj)
        db_obj = self.user_obj.tenant

        request = self.user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(request.data, {u'detail': u'Method "GET" not allowed.'})

    def test_get_object_authenticated_other(self):
        """
        Test that an authenticated user doesn't have access to other tenants.
        """
        set_current_user(self.user_obj)
        db_obj = self.user_obj.tenant

        request = self.other_tenant_user.get(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(request.data, {u'detail': u'Method "GET" not allowed.'})

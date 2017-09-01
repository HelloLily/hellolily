import json

from mock import patch
from rest_framework import status

from lily.billing.models import Billing
from lily.tenant.middleware import set_current_user
from lily.tests.utils import GenericAPITestCase, ElasticSearchFilterAPITest
from lily.users.api.serializers import LilyUserSerializer
from lily.users.factories import LilyUserFactory
from lily.users.models import LilyUser


class LilyUserTests(ElasticSearchFilterAPITest, GenericAPITestCase):
    """
    Class containing tests for the case API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'lilyuser-list'
    detail_url = 'lilyuser-detail'
    factory_cls = LilyUserFactory
    model_cls = LilyUser
    serializer_cls = LilyUserSerializer
    search_attribute = 'full_name'

    def _create_object(self, with_relations=False, size=1, **kwargs):
        return super(LilyUserTests, self)._create_object(
            with_relations=with_relations,
            size=size,
            is_active=True,
            **kwargs
        )

    def _create_object_stub(self, with_relations=False, size=1, with_email=False, **kwargs):
        list_or_dict = super(LilyUserTests, self)._create_object_stub(
            with_relations=with_relations,
            size=size,
            is_active=True,
            **kwargs
        )

        if size > 1:
            for obj in list_or_dict:
                del obj['password']
                if not with_email:
                    del obj['email']
        else:
            del list_or_dict['password']
            if not with_email:
                del list_or_dict['email']

        return list_or_dict

    def test_create_object_tenant_filter(self):
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub(with_email=True)

        request = self.user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_201_CREATED, stub_dict)

        db_obj = self.model_cls.objects.get(pk=request.data.get('id'))
        self.assertEqual(self.user_obj.tenant, db_obj.tenant)

    def test_create_object_authenticated(self):
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub(with_email=True)

        request = self.user.post(self.get_url(self.list_url), stub_dict)
        self.assertStatus(request, status.HTTP_201_CREATED, stub_dict)

        created_id = json.loads(request.content).get('id')
        self.assertIsNotNone(created_id)

        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, json.loads(request.content))

    def test_update_object_authenticated(self):
        set_current_user(self.user_obj)
        stub_dict = self._create_object_stub(with_email=True, email=self.user_obj.email)

        self.user_obj.first_name = 'something'
        self.user_obj.save()

        request = self.user.put(self.get_url(self.detail_url, kwargs={'pk': self.user_obj.pk}), data=stub_dict)
        self.assertStatus(request, status.HTTP_200_OK, stub_dict)

        created_id = request.data.get('id')
        self.assertIsNotNone(created_id)

        db_obj = self.model_cls.objects.get(pk=created_id)
        self._compare_objects(db_obj, request.data)

    @patch.object(Billing, 'update_subscription')
    @patch.object(Billing, 'get_subscription')
    def test_delete_object_authenticated(self, get_subscription_mock, update_subscription_mock):
        set_current_user(self.user_obj)
        db_obj = self._create_object()

        get_subscription_mock.return_value = {
            'subscription': {
                'id': 'L14OolZysKbMfGRY',
                'plan_quantity': 5,
            }
        }

        update_subscription_mock.return_value = True

        request = self.user.delete(self.get_url(self.detail_url, kwargs={'pk': db_obj.pk}))
        self.assertStatus(request, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.model_cls.objects.get(pk=db_obj.pk).is_active)

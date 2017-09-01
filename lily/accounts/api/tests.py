from lily.tenant.factories import TenantFactory
from lily.tests.utils import ElasticSearchFilterAPITest, GenericAPITestCase
from .serializers import AccountSerializer
from ..factories import AccountFactory, AccountStatusFactory, WebsiteFactory
from ..models import Account


class AccountTests(ElasticSearchFilterAPITest, GenericAPITestCase):
    """
    Class containing tests for the accounts API.

    Note that each test removes the 'id' key from the response dict.
    """
    list_url = 'account-list'
    detail_url = 'account-detail'
    factory_cls = AccountFactory
    model_cls = Account
    serializer_cls = AccountSerializer
    search_attribute = 'name'

    def _create_object(self, with_relations=False, size=1, **kwargs):
        data = super(AccountTests, self)._create_object(with_relations, size, **kwargs)

        if size > 1:
            for account in data:
                WebsiteFactory.create_batch(size=2, account=account, tenant=account.tenant)
        else:
            WebsiteFactory.create_batch(size=2, account=data, tenant=data.tenant)

        return data

    def _create_object_stub(self, with_relations=True, size=1, **kwargs):
        """
        Create an object dict with relation dicts using factories.
        """
        # Set a default tenant of the user.
        kwargs['tenant'] = self.user_obj.tenant if not kwargs.get('tenant') else kwargs['tenant']
        object_list = []
        status = AccountStatusFactory(tenant=kwargs['tenant'])

        for iteration in range(0, size):
            obj = self.factory_cls.stub(**kwargs).__dict__
            if with_relations:
                obj['tenant'] = TenantFactory.stub().__dict__
                del obj['tenant']['billing']
                obj['status'] = {'id': status.pk}
            else:
                # Delete the related objects, since they can't be serialized.
                del obj['status']
                del obj['tenant']

            object_list.append(obj)

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def test_patch_with_deletion(self):
        account = self._create_object(with_relations=True)

        data = {}
        fields = {
            'websites': list(account.websites.all()),
        }

        for field_name, object_list in fields.items():
            data[field_name] = [{
                'id': object_list[0].pk,
                'is_deleted': True,
            }, {
                'id': object_list[1].pk,
            }]

        request = self.user.patch(self.get_url(self.detail_url, kwargs={'pk': account.pk}), data)

        for field_name, object_list in fields.items():
            self.assertNotIn(
                object_list[0].pk,
                [item['id'] for item in request.data.get(field_name)],
                '%s %s was -not- deleted while it should have been.' % (field_name, object_list[0].pk)
            )
            self.assertIn(
                object_list[1].pk,
                [item['id'] for item in request.data.get(field_name)],
                '%s %s -was- deleted while it should have been.' % (field_name, object_list[1].pk)
            )

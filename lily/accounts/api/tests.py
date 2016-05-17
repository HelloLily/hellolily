from lily.tenant.factories import TenantFactory
from lily.tests.utils import GenericAPITestCase

from ..factories import AccountFactory, AccountStatusFactory
from ..models import Account
from .serializers import AccountSerializer


class AccountTests(GenericAPITestCase):
    """
    Class containing tests for the accounts API.

    Note that each test removes the 'id' key from the response dict.
    """
    list_url = 'account-list'
    detail_url = 'account-detail'
    factory_cls = AccountFactory
    model_cls = Account
    serializer_cls = AccountSerializer

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

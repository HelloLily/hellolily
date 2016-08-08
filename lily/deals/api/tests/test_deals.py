from lily.accounts.factories import AccountFactory
from lily.deals.api.serializers import DealSerializer
from lily.deals.factories import DealFactory, DealWhyCustomerFactory, DealNextStepFactory, DealFoundThroughFactory, \
    DealContactedByFactory, DealStatusFactory, DealWhyLostFactory
from lily.deals.models import Deal
from lily.notes.factories import NoteFactory
from lily.tags.factories import TagFactory
from lily.tests.utils import GenericAPITestCase
from lily.users.factories import LilyUserFactory


class DealTests(GenericAPITestCase):
    """
    Class containing tests for the deal API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'deal-list'
    detail_url = 'deal-detail'
    factory_cls = DealFactory
    model_cls = Deal
    serializer_cls = DealSerializer

    def _create_object_stub(self, with_relations=False, size=1, **kwargs):
        """
        Create an object dict with relation dicts using factories.
        """
        # Set a default tenant of the user.
        kwargs['tenant'] = self.user_obj.tenant if not kwargs.get('tenant') else kwargs['tenant']

        object_list = []
        account = AccountFactory(**kwargs)
        assigned_to = LilyUserFactory(**kwargs)
        next_step = DealNextStepFactory(**kwargs)
        why_customer = DealWhyCustomerFactory(**kwargs)
        found_through = DealFoundThroughFactory(**kwargs)
        contacted_by = DealContactedByFactory(**kwargs)
        status = DealStatusFactory(**kwargs)
        why_lost = DealWhyLostFactory(**kwargs)

        for iteration in range(0, size):
            obj = self.factory_cls.stub(**kwargs).__dict__
            del obj['tenant']
            del obj['contact']

            # The minimum viable deal instance needs these relations, so always make them.
            obj['account'] = {
                'id': account.pk,
            }
            obj['assigned_to'] = {
                'id': assigned_to.pk,
            }
            obj['next_step'] = {
                'id': next_step.pk,
            }
            obj['why_customer'] = {
                'id': why_customer.pk,
            }
            obj['found_through'] = {
                'id': found_through.pk,
            }
            obj['contacted_by'] = {
                'id': contacted_by.pk,
            }
            obj['status'] = {
                'id': status.pk,
            }
            obj['why_lost'] = {
                'id': why_lost.pk,
            }

            if with_relations:
                # If relations are needed, override them, because a dict is needed instead of an instance.
                obj['tags'] = [TagFactory.stub().__dict__, ]
                obj['notes'] = [NoteFactory.stub().__dict__, ]

            object_list.append(obj)

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def test_create_object_with_relations(self):
        """
        Test that the creation of a deal is successfull with relations.
        """
        pass

    def test_create_object_validation(self):
        """
        Test that the create of a deal is validated properly.
        """
        pass

    def test_update_object_with_relations(self):
        """
        Test that the update of a deal is successfull with relations.
        """
        pass

    def test_update_object_validation(self):
        """
        Test that the update of a deal is validated properly.
        """
        # Update of the object.
        pass

    def test_partial_update_object_with_relations(self):
        """
        Test that the update of a deal is successfull with relations.
        """
        # Partial updates should still validate the related objects.
        # Partial updates should amend to the relations.
        pass

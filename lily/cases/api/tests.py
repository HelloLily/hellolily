from lily.accounts.factories import AccountFactory
from lily.cases.api.serializers import CaseSerializer
from lily.cases.factories import CaseFactory, CaseStatusFactory, CaseTypeFactory
from lily.cases.models import Case
from lily.contacts.factories import ContactFactory
from lily.tests.utils import ElasticSearchFilterAPITest, GenericAPITestCase
from lily.users.factories import LilyUserFactory


class CaseTests(ElasticSearchFilterAPITest, GenericAPITestCase):
    """
    Class containing tests for the case API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'case-list'
    detail_url = 'case-detail'
    factory_cls = CaseFactory
    model_cls = Case
    serializer_cls = CaseSerializer
    search_attribute = 'subject'

    def _create_object_stub(self, with_relations=False, size=1, **kwargs):
        """
        Create an object dict with relation dicts using factories.
        """
        # Set a default tenant of the user.
        kwargs['tenant'] = self.user_obj.tenant if not kwargs.get('tenant') else kwargs['tenant']

        object_list = []
        casetype = CaseTypeFactory(**kwargs)
        casestatus = CaseStatusFactory(**kwargs)

        for iteration in range(0, size):
            obj = self.factory_cls.stub(**kwargs).__dict__
            del obj['tenant']

            # The minimum viable case instance needs these relations, so always make them.
            obj['type'] = {
                'id': casetype.pk
            }
            obj['status'] = {
                'id': casestatus.pk
            }

            if with_relations:
                # If relations are needed, override them, because a dict is needed instead of an instance.
                obj['account'] = AccountFactory.stub().__dict__
                obj['contact'] = ContactFactory.stub().__dict__
                obj['assigned_to'] = LilyUserFactory.stub().__dict__

                del obj['account']['tenant']
                del obj['contact']['tenant']
                del obj['assigned_to']['tenant']
                del obj['created_by']
            else:
                # Delete the related objects, since they can't be serialized.
                del obj['account']
                del obj['assigned_to']
                del obj['created_by']

            object_list.append(obj)

        if size > 1:
            return object_list
        else:
            # If required size is 1, just give the object instead of a list.
            return object_list[0]

    def test_create_object_with_relations(self):
        """
        Test that the creation of a case is successful with relations.
        """
        pass

    def test_create_object_validation(self):
        """
        Test that the create of a case is validated properly.
        """
        pass

    def test_update_object_with_relations(self):
        """
        Test that the update of a case is successful with relations.
        """
        pass

    def test_update_object_validation(self):
        # Update of the object
        pass

    def test_partial_update_object_with_relations(self):
        # Partial updates should still validate the related objects
        # Partial updates should amend to the relations
        pass

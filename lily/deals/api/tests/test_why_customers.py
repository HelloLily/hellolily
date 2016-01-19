from lily.deals.api.serializers import DealWhyCustomerSerializer
from lily.deals.factories import DealWhyCustomerFactory
from lily.deals.models import DealWhyCustomer
from lily.tests.utils import GenericAPITestCase


class DealWhyCustomerTests(GenericAPITestCase):
    """
    Class containing tests for the deal why customer API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'dealwhycustomer-list'
    detail_url = 'dealwhycustomer-detail'
    factory_cls = DealWhyCustomerFactory
    model_cls = DealWhyCustomer
    serializer_cls = DealWhyCustomerSerializer

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

    def test_update_object_validation(self):
        """
        Test that the update of a deal is validated properly.
        """
        # Update of the object.
        pass

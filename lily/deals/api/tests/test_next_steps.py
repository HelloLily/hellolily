from lily.deals.api.serializers import DealNextStepSerializer
from lily.deals.factories import DealNextStepFactory
from lily.deals.models import DealNextStep
from lily.tests.utils import GenericAPITestCase


class DealNextStepTests(GenericAPITestCase):
    """
    Class containing tests for the deal API.

    Note that each test removes the 'id' key from the response dict.
    That's because it's a hassle to compare IDs since they change when the test order is changed.
    """
    list_url = 'dealnextstep-list'
    detail_url = 'dealnextstep-detail'
    factory_cls = DealNextStepFactory
    model_cls = DealNextStep
    serializer_cls = DealNextStepSerializer

    def test_create_object_with_relations(self):
        """
        Test that the creation of a deal is successfull with relations.
        """

    def test_create_object_validation(self):
        """
        Test that the create of a deal is validated properly.
        """

    def test_update_object_validation(self):
        """
        Test that the update of a deal is validated properly.
        """

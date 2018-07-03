from rest_framework.serializers import ModelSerializer

from lily.billing.models import Billing, Plan


class PlanSerializer(ModelSerializer):
    """
    Serializer for the plan model.
    """

    class Meta:
        model = Plan
        fields = (
            'id'
            'name',
            'tier',
        )


class BillingSerializer(ModelSerializer):
    """
    Serializer for the billing model.
    """
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Billing
        fields = (
            'plan',
            'is_free_plan'
        )

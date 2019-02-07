from rest_framework.exceptions import PermissionDenied

from lily.api.nested.serializers import WritableNestedSerializer
from lily.billing.api.serializer import BillingSerializer
from lily.integrations.api.serializers import RelatedIntegrationSerializer
from lily.tenant.models import Tenant
from lily.utils.api.serializers import RelatedExternalAppLinkSerializer
from lily.utils.functions import has_required_tier


class TenantSerializer(WritableNestedSerializer):
    """
    Serializer for the tenant model.
    """
    external_app_links = RelatedExternalAppLinkSerializer(read_only=True, many=True, source='externalapplink_set')
    integrations = RelatedIntegrationSerializer(read_only=True, many=True, source='integrationdetails_set')
    billing = BillingSerializer(read_only=True)

    def update(self, instance, validated_data):
        if not self.context.get('request').user.is_admin:
            raise PermissionDenied

        if not has_required_tier(1):
            # Settings only allowed for 'Team' plan and higher.
            team_features = ['timelogging_enabled', 'billing_default']

            # Tenant doesn't have the required tier, so check if their API request
            # contains any of the blocked settings.
            if any(x in validated_data for x in team_features):
                raise PermissionDenied

        return super(TenantSerializer, self).update(instance, validated_data)

    class Meta:
        model = Tenant
        fields = (
            'id',
            'billing_default',
            'billing',
            'currency',
            'external_app_links',
            'integrations',
            'name',
            'timelogging_enabled',
        )

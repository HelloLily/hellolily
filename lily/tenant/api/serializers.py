from lily.api.nested.serializers import WritableNestedSerializer
from lily.integrations.api.serializers import RelatedIntegrationSerializer
from lily.tenant.models import Tenant
from lily.utils.api.serializers import RelatedExternalAppLinkSerializer


class TenantSerializer(WritableNestedSerializer):
    """
    Serializer for the tenant model.
    """
    external_app_links = RelatedExternalAppLinkSerializer(read_only=True, many=True, source='externalapplink_set')
    integrations = RelatedIntegrationSerializer(read_only=True, many=True, source='integrationdetails_set')

    class Meta:
        model = Tenant
        fields = (
            'id',
            'name',
            'external_app_links',
            'integrations',
            'currency',
        )

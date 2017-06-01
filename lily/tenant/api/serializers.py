from rest_framework.exceptions import PermissionDenied

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

    def update(self, instance, validated_data):
        if not self.context.get('request').user.is_admin:
            raise PermissionDenied

        return super(TenantSerializer, self).update(instance, validated_data)

    class Meta:
        model = Tenant
        fields = (
            'id',
            'billing_default',
            'currency',
            'external_app_links',
            'integrations',
            'name',
            'timelogging_enabled',
        )

from lily.tenant.models import Tenant
from lily.utils.api.related.serializers import WritableNestedSerializer
from lily.utils.api.serializers import RelatedExternalAppLinkSerializer


class TenantSerializer(WritableNestedSerializer):
    """
    Serializer for the tenant model.
    """
    external_app_links = RelatedExternalAppLinkSerializer(read_only=True, many=True, source='externalapplink_set')

    class Meta:
        model = Tenant
        fields = (
            'id',
            'name',
            'external_app_links',
        )

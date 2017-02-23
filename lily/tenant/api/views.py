from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from lily.tenant.api.serializers import TenantSerializer
from lily.tenant.models import Tenant


class TenantViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Returns a list of all tenants in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Filtering#
    Filtering is enabled on this API.

    To filter, use the field name as parameter name followed by the value you want to filter on.

    The following fields can be filtered on the exact value and

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/tenants/`
    - search: `/api/tenants/?search=subject:Doremi`
    - filter: `/api/tenants/?type=1`
    - order: `/api/tenants/?ordering=subject,-id`

    #Returns#
    * List of tenants with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Tenant.objects
    # Set the serializer class for this viewset.
    serializer_class = TenantSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = ()
    # Disable pagination for this api.
    pagination_class = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant.
        """
        return super(TenantViewSet, self).get_queryset().filter(pk=self.request.user.tenant_id)

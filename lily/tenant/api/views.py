from rest_framework import mixins
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from lily.tenant.api.serializers import TenantSerializer
from lily.tenant.models import Tenant
from lily.users.api.serializers import LilyUserSerializer


class TenantViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Tenant.objects
    # Set the serializer class for this viewset.
    serializer_class = TenantSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = ()
    # Disable pagination for this api.
    pagination_class = None
    swagger_schema = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant.
        """
        return super(TenantViewSet, self).get_queryset().filter(pk=self.request.user.tenant_id)

    @list_route(methods=['GET'])
    def admin(self, request):
        account_admin = request.user.tenant.admin

        context = self.get_serializer_context()
        serializer = LilyUserSerializer(instance=account_admin, context=context)

        return Response({'admin': serializer.data})

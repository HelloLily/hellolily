from django.conf import settings
from netaddr import IPAddress, IPNetwork
from rest_framework import mixins, viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from lily.voipgrid.api.serializers import CallNotificationSerializer


class VoipgridIpAddress(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """
    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']

        return IPAddress(ip_addr) in IPNetwork(settings.VOIPGRID_IPS) or any([settings.DEBUG, settings.TESTING, ])


class CallNotificationViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    # Set the serializer class for this viewset.
    serializer_class = CallNotificationSerializer
    # Set the permission class to only allow vg ips.
    permission_classes = (IsAuthenticated, VoipgridIpAddress, )

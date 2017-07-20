from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from email_wrapper_lib.models import EmailAccount
from lily.email.api.filters import EmailAccountFilter
from lily.email.api.serializers import EmailAccountSerializer


class EmailAccountViewSet(ModelViewSet):
    """
    Returns a list of all **active** email accounts in the system.
    """
    # Set the queryset.
    queryset = EmailAccount.objects
    # Set the serializer class for this viewset.
    serializer_class = EmailAccountSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter, DjangoFilterBackend,)

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('id',)
    # OrderingFilter: set the default ordering fields.
    ordering = ('id',)
    # DjangoFilter: set the filter class.
    filter_class = EmailAccountFilter

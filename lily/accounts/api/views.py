from rest_framework import viewsets
from lily.accounts.api.serializers import AccountSerializer
from lily.accounts.models import Account


class AccountViewSet(viewsets.ModelViewSet):
    """
    This viewset contains all possible ways to manipulate an Account.
    """
    queryset = Account.objects  # Without .all() this filters on the tenant
    serializer_class = AccountSerializer

    def get_queryset(self):
        return super(AccountViewSet, self).get_queryset().filter(is_deleted=False)

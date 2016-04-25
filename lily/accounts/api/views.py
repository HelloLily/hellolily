from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import MultiSerializerViewSetMixin
from lily.utils.api.views import (AddressViewSet, EmailAddressViewSet, PhoneNumberViewSet, RelatedModelViewSet,
                                  TagViewSet)
from lily.tenant.api.mixins import SetTenantUserMixin
from .serializers import AccountSerializer, AccountCreateSerializer, WebsiteSerializer, AccountStatusSerializer
from ..models import Account, Website, AccountStatus


class AccountViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** accounts in the system.

    #Search#
    Searching is enabled on this API.

    Example:
    `/api/accounts/account/?search=name:CompanyA`

    #Returns#
    * List of accounts with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Account.objects
    serializer_class = AccountSerializer
    serializer_action_classes = {
        'create': AccountCreateSerializer,
        'update': AccountCreateSerializer,
        'partial_update': AccountCreateSerializer,
        'options': AccountCreateSerializer,
    }
    filter_backends = (ElasticSearchFilter,)
    model_type = 'accounts_account'

    def get_queryset(self):
        return super(AccountViewSet, self).get_queryset().filter(is_deleted=False)


class WebsiteViewSet(RelatedModelViewSet):
    queryset = Website.objects
    serializer_class = WebsiteSerializer
    related_model = Account

    def _get_related_queryset(self, object_pk):
        return self._get_related_object(object_pk).websites


class AccountPhoneNumberViewSet(PhoneNumberViewSet):
    related_model = Account


class AccountAddressViewSet(AddressViewSet):
    related_model = Account


class AccountEmailAddressViewSet(EmailAddressViewSet):
    related_model = Account


class AccountTagViewSet(TagViewSet):
    related_model = Account


class AccountStatusViewSet(SetTenantUserMixin, ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = AccountStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountStatusSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(AccountStatusViewSet, self).get_queryset().all()

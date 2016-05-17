import django_filters

from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.utils.api.views import (AddressViewSet, EmailAddressViewSet, PhoneNumberViewSet, RelatedModelViewSet,
                                  TagViewSet)
from lily.tenant.api.mixins import SetTenantUserMixin
from .serializers import AccountSerializer, WebsiteSerializer, AccountStatusSerializer
from ..models import Account, Website, AccountStatus


class AccountFilter(django_filters.FilterSet):
    class Meta:
        model = Account
        fields = {
            'addresses': ['exact', ],
            'assigned_to': ['exact', ],
            'bankaccountnumber': ['exact', ],
            'bic': ['exact', ],
            'cocnumber': ['exact', ],
            'contacts': ['exact', ],
            'created': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'customer_id': ['exact', ],
            'description': ['exact', ],
            'email_addresses': ['exact', ],
            'flatname': ['exact', ],
            'iban': ['exact', ],
            'legalentity': ['exact', ],
            'logo': ['exact', ],
            'id': ['exact', ],
            'modified': ['exact', ],
            'name': ['exact', ],
            'phone_numbers': ['exact', ],
            'social_media': ['exact', ],
            'status': ['exact', ],
            'tags': ['exact', ],
            'taxnumber': ['exact', ],
            'websites': ['exact', ],
        }


class AccountViewSet(SetTenantUserMixin, ModelViewSet):
    """
    Returns a list of all **active** accounts in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want
    to search for to the search parameter.

    #Returns#
    * List of accounts with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Account.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend, )

    # ElasticSearchFilter: set the model type.
    model_type = 'accounts_account'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('id', )
    # OrderingFilter: set the default ordering fields.
    ordering = ('id', )
    # DjangoFilter: set the filter class.
    filter_class = AccountFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
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

from rest_framework import viewsets

from lily.api.mixins import MultiSerializerViewSetMixin
from lily.tags.api.views import TagViewSet
from lily.utils.api.views import AddressViewSet, EmailAddressViewSet, PhoneNumberViewSet, RelatedModelViewSet
from .serializers import AccountSerializer, AccountCreateSerializer, WebsiteSerializer
from ..models import Account, Website


class AccountViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    """
    This viewset contains all possible ways to manipulate an Account.
    """
    queryset = Account.objects  # Without .all() this filters on the tenant
    serializer_class = AccountSerializer
    serializer_action_classes = {
        'create': AccountCreateSerializer,
        'options': AccountCreateSerializer,
    }

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

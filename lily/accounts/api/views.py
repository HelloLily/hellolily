from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import detail_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin
from lily.calls.api.serializers import CallSerializer
from lily.calls.models import Call
from lily.users.models import LilyUser

from .serializers import AccountSerializer, AccountStatusSerializer
from ..models import Account, AccountStatus


class AccountFilter(FilterSet):
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
            'id': ['exact', ],
            'modified': ['exact', ],
            'name': ['exact', ],
            'phone_numbers': ['exact', ],
            'social_media': ['exact', ],
            'status': ['exact', ],
            'taxnumber': ['exact', ],
            'websites': ['exact', ],
        }


class AccountViewSet(ModelChangesMixin, ModelViewSet):
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
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') == 'False':
                return super(AccountViewSet, self).get_queryset()

        return super(AccountViewSet, self).get_queryset().filter(is_deleted=False)

    @detail_route(methods=['GET'])
    def calls(self, request, pk=None):
        """
        Gets the calls for the given contact.
        """
        account_phone_numbers = []
        calls = []
        account = self.get_object()
        contacts = account.get_contacts()

        # Get calls made from a phone number which belongs to the account.
        for number in account.phone_numbers.all():
            account_phone_numbers.append(number.number)

        call_objects = Call.objects.filter(
            status=Call.ANSWERED,
            type=Call.INBOUND,
            caller_number__in=account_phone_numbers,
            created__isnull=False,
        )

        if call_objects:
            calls = CallSerializer(call_objects, many=True).data

            for call in calls:
                call['account'] = account.name

                if len(contacts) == 1:
                    call['contact'] = contacts[0].full_name

                user = LilyUser.objects.filter(internal_number=call.get('internal_number')).first()

                if user:
                    call['user'] = user.full_name

        # Get calls for every phone number of every contact in an account.
        for contact in contacts:
            contact_phone_numbers = []

            for number in contact.phone_numbers.all():
                contact_phone_numbers.append(number.number)

            call_objects = Call.objects.filter(
                status=Call.ANSWERED,
                type=Call.INBOUND,
                caller_number__in=contact_phone_numbers,
                created__isnull=False,
            )

            if call_objects:
                contact_calls = CallSerializer(call_objects, many=True).data

                for call in contact_calls:
                    call['contact'] = contact.full_name

                    user = LilyUser.objects.filter(internal_number=call.get('internal_number')).first()

                    if user:
                        call['user'] = user.full_name

                    calls.append(call)

        return Response({'objects': calls})


class AccountStatusViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = AccountStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountStatusSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(AccountStatusViewSet, self).get_queryset().all()

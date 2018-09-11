from django.db.models import Q
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import detail_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, DataExistsMixin, NoteMixin
from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.utils.functions import uniquify
from .serializers import AccountSerializer, AccountStatusSerializer
from ..models import Account, AccountStatus


class AccountFilter(filters.FilterSet):
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


class AccountViewSet(ModelChangesMixin, DataExistsMixin, NoteMixin, ModelViewSet):
    """
    Accounts are companies you've had contact with and for which you wish to store information.

    retrieve:
    Returns the given account.

    list:
    Returns a list of all the existing active accounts.

    create:
    Creates a new account.

    update:
    Overwrites the whole account with the given data.

    partial_update:
    Updates just the fields in the request data of the given account.

    delete:
    Deletes the given account.

    changes:
    Returns all the changes performed on the given account.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Account.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, filters.DjangoFilterBackend, )

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

    @swagger_auto_schema(auto_schema=None)
    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        account = self.get_object()

        phone_numbers = list(account.phone_numbers.all().values_list('number', flat=True))

        contact_list = account.get_contacts()

        for contact in contact_list:
            phone_numbers += list(contact.phone_numbers.all().values_list('number', flat=True))

        phone_numbers = uniquify(phone_numbers)  # Filter out double numbers.

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        ).order_by(
            '-start'
        )[:100]

        serializer = CallRecordSerializer(calls, many=True, context={'request': request})

        return Response({'results': serializer.data})


class AccountStatusViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = AccountStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = AccountStatusSerializer
    swagger_schema = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(AccountStatusViewSet, self).get_queryset().all()

                {'file_accounts': {'The following columns are missing: {0}'.format(', '.join(missing_in_upload))}},
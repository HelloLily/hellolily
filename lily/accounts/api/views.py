from django.db.models import Q
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import detail_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, DataExistsMixin, ElasticModelMixin, NoteMixin
from lily.calls.api.serializers import CallRecordSerializer
from lily.calls.models import CallRecord
from lily.utils.models.models import PhoneNumber
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


class AccountViewSet(ElasticModelMixin, ModelChangesMixin, DataExistsMixin, NoteMixin, ModelViewSet):
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
    queryset = Account.elastic_objects
    # Set the serializer class for this viewset.
    serializer_class = AccountSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, filters.DjangoFilterBackend, )
    search_fields = ('name', )

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('name', 'status__name', 'created', 'modified', 'assigned_to__first_name')
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('assigned_to', 'description', 'email_addresses', 'name', 'phone_numbers', 'status', 'tags',
                     'websites')
    # DjangoFilter: set the filter class.
    filter_class = AccountFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        if 'filter_deleted' in self.request.GET:
            if self.request.GET.get('filter_deleted') in ['False', 'false']:
                return super(AccountViewSet, self).get_queryset()

        return super(AccountViewSet, self).get_queryset().filter(is_deleted=False)

    @swagger_auto_schema(auto_schema=None)
    @detail_route(methods=['GET', ])
    def calls(self, request, pk=None):
        account = self.get_object()
        contact_list = account.get_contacts()

        # Get all the unique phone numbers of the account and of it's contacts as a flat list.
        phone_numbers = account.phone_numbers.all()
        phone_numbers |= PhoneNumber.objects.filter(contact__in=contact_list)
        phone_numbers = list(phone_numbers.values_list('number', flat=True).distinct())

        calls = CallRecord.objects.filter(
            Q(caller__number__in=phone_numbers) | Q(destination__number__in=phone_numbers)
        ).prefetch_related(
            'caller',
            'destination',
            'transfers',
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

from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, TimeLogMixin

from .serializers import (DealSerializer, DealNextStepSerializer, DealWhyCustomerSerializer, DealWhyLostSerializer,
                          DealFoundThroughSerializer, DealContactedBySerializer, DealStatusSerializer)
from ..models import Deal, DealNextStep, DealWhyCustomer, DealWhyLost, DealFoundThrough, DealContactedBy, DealStatus


class DealContactedByList(APIView):
    def get(self, request, format=None):
        return Response(Deal.CONTACTED_BY_CHOICES)


class DealNextStepList(APIView):
    model = DealNextStep
    serializer_class = DealNextStepSerializer

    def get(self, request, format=None):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        serializer = DealNextStepSerializer(queryset, many=True)
        return Response(serializer.data)


class DealWhyCustomerViewSet(ModelViewSet):
    # Set the queryset, this takes care of setting the `base_name`.
    queryset = DealWhyCustomer.objects
    # Set the serializer class for this viewset.
    serializer_class = DealWhyCustomerSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealWhyCustomerViewSet, self).get_queryset().all()


class DealWhyLostViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = DealWhyLost.objects
    serializer_class = DealWhyLostSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealWhyLostViewSet, self).get_queryset().all()


class DealNextStepViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = DealNextStep.objects
    # Set the serializer class for this viewset.
    serializer_class = DealNextStepSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealNextStepViewSet, self).get_queryset().all()


class DealFoundThroughViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = DealFoundThrough.objects
    # Set the serializer class for this viewset.
    serializer_class = DealFoundThroughSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealFoundThroughViewSet, self).get_queryset().all()


class DealContactedByViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = DealContactedBy.objects
    # Set the serializer class for this viewset.
    serializer_class = DealContactedBySerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealContactedByViewSet, self).get_queryset().all()


class DealStatusViewSet(ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = DealStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = DealStatusSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealStatusViewSet, self).get_queryset().all()


class DealFilter(FilterSet):
    class Meta:
        model = Deal
        fields = {
            'account': ['exact', ],
            'amount_once': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'amount_recurring': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'assigned_to': ['exact', ],
            'card_sent': ['exact', ],
            'closed_date': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'contacted_by': ['exact', ],
            'created': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'currency': ['exact', ],
            'found_through': ['exact', ],
            'is_checked': ['exact', ],
            'modified': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'name': ['exact', ],
            'new_business': ['exact', ],
            'next_step': ['exact', ],
            'next_step_date': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'quote_id': ['exact', ],
            'status': ['exact', ],
            'twitter_checked': ['exact', ],
            'why_customer': ['exact', ],
            'why_lost': ['exact', ],
        }


class DealViewSet(ModelChangesMixin, TimeLogMixin, ModelViewSet):
    """
    Returns a list of all **active** deals in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Filtering#
    Filtering is enabled on this API.

    To filter, use the field name as parameter name followed by the value you want to filter on.

    The following fields can be filtered on the exact value and

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/deals/`
    - search: `/api/deals/?search=subject:Doremi`
    - filter: `/api/deals/?type=1`
    - order: `/api/deals/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Deal.objects
    # Set the serializer class for this viewset.
    serializer_class = DealSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend, )

    # ElasticSearchFilter: set the model type.
    model_type = 'deals_deal'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('id', )
    # OrderingFilter: set the default ordering fields.
    ordering = ('id', )
    # DjangoFilter: set the filter class.
    filter_class = DealFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(DealViewSet, self).get_queryset().filter(is_deleted=False)

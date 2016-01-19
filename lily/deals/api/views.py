import django_filters

from rest_framework.filters import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lily.api.filters import ElasticSearchFilter
from lily.tenant.api.mixins import SetTenantUserMixin

from .serializers import DealSerializer, DealNextStepSerializer, DealWhyCustomerSerializer
from ..models import Deal, DealNextStep, DealWhyCustomer


class DealStagesList(APIView):
    def get(self, request, format=None):
        return Response(Deal.STAGE_CHOICES)


class DealNextStepList(APIView):
    model = DealNextStep
    serializer_class = DealNextStepSerializer

    def get(self, request, format=None):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        serializer = DealNextStepSerializer(queryset, many=True)
        return Response(serializer.data)


class DealWhyCustomerViewSet(SetTenantUserMixin, ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant.
    queryset = DealWhyCustomer.objects
    # Set the serializer class for this viewset.
    serializer_class = DealWhyCustomerSerializer


class DealNextStepViewSet(SetTenantUserMixin, ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant.
    queryset = DealNextStep.objects
    # Set the serializer class for this viewset.
    serializer_class = DealNextStepSerializer


class DealFilter(django_filters.FilterSet):
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
            'feedback_form_sent': ['exact', ],
            'found_through': ['exact', ],
            'is_checked': ['exact', ],
            'modified': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'name': ['exact', ],
            'new_business': ['exact', ],
            'next_step': ['exact', ],
            'next_step_date': ['exact', 'lt', 'lte', 'gt', 'gte', ],
            'quote_id': ['exact', ],
            'stage': ['exact', ],
            'twitter_checked': ['exact', ],
            'why_customer': ['exact', ],
        }


class DealViewSet(SetTenantUserMixin, ModelViewSet):
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
    - plain: `/api/cases/case/`
    - search: `/api/cases/case/?search=subject:Doremi`
    - filter: `/api/cases/case/?type=1`
    - order: `/api/cases/case/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant.
    queryset = Deal.objects
    # Set the serializer class for this viewset.
    serializer_class = DealSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend,)

    # ElasticSearchFilter: set the model type.
    model_type = 'deals_deal'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('id', )
    # OrderingFilter: set the default ordering fields.
    ordering = ('id', )
    # DjangoFilter: set the filter class.
    filter_class = DealFilter

    def get_queryset(self):
        return super(DealViewSet, self).get_queryset().filter(is_deleted=False)

from django_filters import FilterSet, CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from lily.api.filters import ElasticSearchFilter
from lily.tenant.api.mixins import SetTenantUserMixin
from .serializers import CaseSerializer, CaseStatusSerializer, CaseTypeSerializer
from ..models import Case, CaseStatus, CaseType


def queryset_filter(request, queryset):
    """
    General queryset filter being used by all views in this file.
    """
    is_assigned = request.GET.get('is_assigned', None)
    # Ugly filter hack due to not functioning django-filters booleanfilter.
    if is_assigned is not None:
        is_assigned = is_assigned == 'False'
        queryset = queryset.filter(assigned_to__isnull=is_assigned)

    is_archived = request.GET.get('is_archived', None)
    # Ugly filter hack due to not functioning django-filters booleanfilter.
    if is_archived is not None:
        is_archived = is_archived == 'False'
        queryset = queryset.filter(is_archived=is_archived)

    return queryset


class CaseFilter(FilterSet):
    """
    Class to filter case queryset.
    """
    type = CharFilter(name='type__type')
    status = CharFilter(name='status__status')
    not_type = CharFilter(name='type__type', exclude=True)
    not_status = CharFilter(name='status__status', exclude=True)

    class Meta:
        model = Case
        fields = ['type', 'status', 'not_type', 'not_status', ]


class CaseViewSet(SetTenantUserMixin, viewsets.ModelViewSet):
    """
    Returns a list of all **active** cases in the system.

    #Search#
    Searching is enabled on this API.

    To search, provide a field name to search on followed by the value you want to search for to the search parameter.

    #Filtering#
    Filtering is enabled on this API.

    To filter, use the field name as parameter name followed by the value you want to filter on.

    #Ordering#
    Ordering is enabled on this API.

    To order, provide a comma seperated list to the ordering argument. Use `-` minus to inverse the ordering.

    #Examples#
    - plain: `/api/cases/`
    - search: `/api/cases/?search=subject:Doremi`
    - filter: `/api/cases/?type=1`
    - order: `/api/cases/?ordering=subject,-id`

    #Returns#
    * List of cases with related fields
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Case.objects
    # Set the serializer class for this viewset.
    serializer_class = CaseSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, DjangoFilterBackend,)

    # ElasticSearchFilter: set the model type.
    model_type = 'cases_case'
    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('id', 'created', 'modified', 'priority', 'subject',)
    # OrderingFilter: set the default ordering fields.
    ordering = ('id',)
    # DjangoFilter: set the filter class.
    filter_class = CaseFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        queryset = super(CaseViewSet, self).get_queryset().filter(is_deleted=False)
        return queryset_filter(self.request, queryset)


class TeamsCaseList(APIView):
    """
    List all cases assigned to the current users teams.
    """
    model = Case
    serializer_class = CaseSerializer
    filter_class = CaseFilter

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        queryset = queryset_filter(self.request, queryset)
        return queryset

    def get(self, request, pk=None, format=None):
        if pk is None:
            pk = self.request.user.teams.all()
        queryset = self.get_queryset().filter(assigned_to_teams=pk)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset)
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class CaseStatusViewSet(SetTenantUserMixin, viewsets.ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = CaseStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = CaseStatusSerializer

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(CaseStatusViewSet, self).get_queryset().all()


class CaseTypeList(APIView):
    model = CaseType
    serializer_class = CaseTypeSerializer

    def get(self, request, format=None):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        serializer = CaseTypeSerializer(queryset, many=True)
        return Response(serializer.data)

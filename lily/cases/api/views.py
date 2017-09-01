from django.db.models import Q
from django_filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django_filters.rest_framework import BooleanFilter, DateFilter, DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_filters import FilterSet

from lily.api.filters import ElasticSearchFilter
from lily.api.mixins import ModelChangesMixin, TimeLogMixin, DataExistsMixin, NoteMixin

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


class CaseFilter(filters.FilterSet):
    """
    Class to filter case queryset.
    """
    type = CharFilter(name='type__type')
    status = CharFilter(name='status__status')
    not_type = CharFilter(name='type__type', exclude=True)
    not_status = CharFilter(name='status__status', exclude=True)
    is_archived = BooleanFilter()
    is_assigned = BooleanFilter()
    expires = DateFilter()

    class Meta:
        model = Case
        fields = {
            'type': ['exact'],
            'status': ['exact'],
            'not_type': ['exact'],
            'not_status': ['exact'],
            'is_archived': ['exact'],
            'expires': ['exact', 'gte', 'lte', 'lt', 'gt'],
            'account__id': ['exact'],
        }


class CaseViewSet(ModelChangesMixin, TimeLogMixin, DataExistsMixin, NoteMixin, viewsets.ModelViewSet):
    """
    retrieve:
    Returns the given case.

    list:
    Returns a list of all cases.

    create:
    Creates a new case.

    update:
    Overwrites the whole case with the given data.

    ***

    > Note: The case is automatically archived if the status is set to 'Closed'.

    partial_update:
    Updates just the fields in the request data of the given case.

    ***

    > <label>Note:</label> The case is automatically archived if the status is set to 'Closed'.

    delete:
    Deletes the given case.

    changes:
    Returns all the changes performed on the given case.

    timelogs:
    Returns all timelogs for the given case.
    """
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = Case.elastic_objects
    # Set the serializer class for this viewset.
    serializer_class = CaseSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (ElasticSearchFilter, OrderingFilter, filters.DjangoFilterBackend,)

    # OrderingFilter: set all possible fields to order by.
    ordering_fields = ('created', 'modified', 'type', 'status', 'assigned_to', 'priority', 'subject', 'expires',
                       'created_by__first_name', )
    # SearchFilter: set the fields that can be searched on.
    search_fields = ('account', 'contact', 'assigned_to', 'created_by', 'status', 'subject', 'tags', 'type', )
    # DjangoFilter: set the filter class.
    filter_class = CaseFilter

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        queryset = super(CaseViewSet, self).get_queryset().filter(is_deleted=False)
        return queryset_filter(self.request, queryset)

    @swagger_auto_schema(auto_schema=None)
    @list_route(methods=['GET'])
    def open(self, request):
        account = request.GET.get('account')
        contact = request.GET.get('contact')

        closed_status = CaseStatus.objects.get(name='Closed')

        cases = Case.objects.filter(is_archived=False, is_deleted=False).exclude(status=closed_status)

        if account and contact:
            cases = cases.filter(Q(account_id=account) | Q(contact_id=contact))
        elif account:
            cases = cases.filter(account_id=account)
        elif contact:
            cases = cases.filter(contact_id=contact)

        serializer = CaseSerializer(cases, many=True)

        return Response({'results': serializer.data})


class TeamsCaseList(APIView):
    """
    List all cases assigned to the current users teams.
    """
    model = Case
    serializer_class = CaseSerializer
    filter_class = CaseFilter
    swagger_schema = None

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        queryset = queryset_filter(self.request, queryset)
        return queryset


class CaseStatusViewSet(viewsets.ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes care of setting the `base_name`.
    queryset = CaseStatus.objects
    # Set the serializer class for this viewset.
    serializer_class = CaseStatusSerializer
    swagger_schema = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        return super(CaseStatusViewSet, self).get_queryset().all()


class CasePrioritiesList(APIView):
    def get(self, request, format=None):
        priorities = Case.PRIORITY_CHOICES
        date_increments = [5, 3, 1, 0]
        results = []

        for priority in priorities:
            value = priority[0]

            results.append({
                'id': value,
                'name': priority[1],
                'date_increment': date_increments[value]
            })

        return Response({'results': results})


class CaseTypeViewSet(viewsets.ModelViewSet):
    model = CaseType
    queryset = CaseType.objects
    serializer_class = CaseTypeSerializer
    swagger_schema = None

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant and works with pagination.
        """
        queryset = super(CaseTypeViewSet, self).get_queryset().filter(tenant_id=self.request.user.tenant_id)

        # By default we filter out non-active case types.
        is_archived = self.request.query_params.get('is_archived', 'False')

        # Value must be one of these, or it is ignored and we filter out non-active users.
        if is_archived not in ['All', 'True', 'False']:
            is_archived = 'False'

        if is_archived in ['True', 'False']:
            queryset = queryset.filter(is_archived=(is_archived == 'True'))
        else:
            queryset = queryset.order_by('is_archived')

        return queryset

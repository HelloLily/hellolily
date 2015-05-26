import django_filters
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .serializers import CaseSerializer, CaseStatusSerializer
from ..models import Case, CaseStatus


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


class CaseFilter(django_filters.FilterSet):
    """
    Class to filter case queryset.
    """
    type = django_filters.CharFilter(name='type__type')
    status = django_filters.CharFilter(name='status__status')
    not_type = django_filters.CharFilter(name='type__type', exclude=True)
    not_status = django_filters.CharFilter(name='status__status', exclude=True)

    class Meta:
        model = Case
        fields = ['type', 'status', 'not_type', 'not_status', 'is_deleted']


class CaseViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    """
    List all cases for a tenant.
    """
    filter_class = CaseFilter
    model = Case
    serializer_class = CaseSerializer
    queryset = Case.objects  # Without .all() this filters on the tenant

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        queryset = queryset_filter(self.request, queryset)
        return queryset

    def get(self, request, format=None):
        filtered_queryset = self.filter_class(request.GET, queryset=self.get_queryset())
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        case = Case.objects.get(pk=kwargs.get('pk'))
        serializer = CaseSerializer(case, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class UserCaseList(APIView):
    """
    List all cases of the user based on PK.
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
            pk = self.request.user.id
        queryset = self.get_queryset().filter(assigned_to=pk)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset)
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


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
            pk = self.request.user.lily_groups.all()
        queryset = self.get_queryset().filter(assigned_to_groups=pk)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset)
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class CaseStatusList(APIView):
    model = CaseStatus
    serializer_class = CaseStatusSerializer

    def get(self, request, format=None):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        serializer = CaseStatusSerializer(queryset, many=True)
        return Response(serializer.data)

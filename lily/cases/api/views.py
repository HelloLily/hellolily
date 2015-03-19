import django_filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CaseSerializer
from ..models import Case


def assigned_to_filter(request, queryset):
    """
    Ugly filter hack due to not functioning django-fitlers booleanfilter.
    """
    is_assigned = request.GET.get('is_assigned', None)
    if is_assigned is not None:
        is_assigned = is_assigned == "False"
        queryset = queryset.filter(assigned_to__isnull=is_assigned)
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
        fields = ['type', 'status', 'not_type', 'not_status']


class CaseList(APIView):
    """
    List all cases for a tenant.
    """
    model = Case
    serializer_class = CaseSerializer
    filter_class = CaseFilter

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        queryset = assigned_to_filter(self.request, queryset)
        return queryset

    def get(self, request, format=None):
        filtered_queryset = self.filter_class(request.GET, queryset=self.get_queryset())
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
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
        queryset = assigned_to_filter(self.request, queryset)
        return queryset

    def get(self, request, pk=None, format=None):
        if pk is None:
            pk = self.request.user.id
        queryset = self.get_queryset().filter(assigned_to=pk)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset)
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class TeamCaseList(APIView):
    """
    List all cases assigned to the current users teams.
    """
    model = Case
    serializer_class = CaseSerializer
    filter_class = CaseFilter

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id,
                                             assigned_to_groups=self.request.user.lily_groups.all())
        queryset = assigned_to_filter(self.request, queryset)
        return queryset

    def get(self, request, format=None):
        filtered_queryset = self.filter_class(request.GET, queryset=self.get_queryset())
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)

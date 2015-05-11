import django_filters
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from lily.users.models import LilyUser

from .serializers import CaseSerializer, CaseStatusSerializer
from ..models import Case, CaseStatus


# class CaseDetail(viewsets.ModelViewSet):
#     queryset = Case.objects
#     serializer_class = CaseSerializer
#
#     # def get(self, request, *args, **kwargs):
#     #     return self.retrieve(request, *args, **kwargs)
#     #
#     # def patch(self, request, *args, **kwargs):
#     #     # case = Case.objects.get(pk=kwargs.get('pk'))
#     #     # assignee = request.data.get('assigned_to')
#     #     #
#     #     # serializer = CaseSerializer(case, data=request.data)
#     #     #
#     #     # import ipdb
#     #     # ipdb.set_trace()
#     #     #
#     #     # if assignee:
#     #     #     try:
#     #     #         user = LilyUser.objects.get(pk=request.data.get('assigned_to'), tenant=self.request.user.tenant)
#     #     #     except LilyUser.DoesNotExist:
#     #     #         return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
#     #     #
#     #     # # user = self.get_object(pk)
#     #     # # serializer = UserSerializer(user, data=request.DATA)
#     #     # # if serializer.is_valid():
#     #     # #     serializer.save()
#     #     # #     return Response(serializer.data)
#     #     # # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     #     return self.partial_update(request, *args, **kwargs)
#
#     def get_queryset(self):
#         return super(CaseDetail, self).get_queryset().filter(is_deleted=False)


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
    model = Case
    serializer_class = CaseSerializer
    filter_class = CaseFilter

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        queryset = queryset_filter(self.request, queryset)
        return queryset

    def get(self, request, format=None):
        filtered_queryset = self.filter_class(request.GET, queryset=self.get_queryset())
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        assignee = request.data.get('assigned_to', None)
        case = Case.objects.get(pk=kwargs.get('pk'))
        serializer = CaseSerializer(case, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            # For now manually check if assignee belongs to tenant
            # In the future we can hopefully implement a generic solution
            if assignee:
                try:
                    LilyUser.objects.get(pk=request.data.get('assigned_to'), tenant=request.user.tenant)
                except LilyUser.DoesNotExist:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

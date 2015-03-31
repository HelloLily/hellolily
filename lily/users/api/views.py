import django_filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LilyGroupSerializer, LilyUserSerializer
from ..models import LilyGroup, LilyUser


class TeamFilter(django_filters.FilterSet):
    """
    Class to filter case queryset.
    """

    class Meta:
        model = LilyGroup
        fields = ['name', ]


class TeamList(APIView):
    """
    List all teams assigned to the current user.
    """
    model = LilyGroup
    serializer_class = LilyGroupSerializer
    filter_class = TeamFilter

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id, user=self.request.user)
        return queryset

    def get(self, request, format=None):
        filtered_queryset = self.filter_class(request.GET, queryset=self.get_queryset())
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class LilyUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LilyUserSerializer
    model = LilyUser

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        return queryset

import django_filters
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied
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


class LilyUserViewSet(mixins.UpdateModelMixin,
                      viewsets.ReadOnlyModelViewSet):
    serializer_class = LilyUserSerializer
    model = LilyUser

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        return queryset

    def get_object(self):
        """
        Get a user by pk

        If the pk is set to 'me', the currently logged in user will be returned

        Returns:
            serialized user instance
        """
        if self.kwargs['pk'] == 'me':
            return self.request.user
        else:
            return super(LilyUserViewSet, self).get_object()

    def update(self, request, *args, **kwargs):
        if self.request.user != self.get_object():
            raise PermissionDenied

        return super(LilyUserViewSet, self).update(request, args, kwargs)

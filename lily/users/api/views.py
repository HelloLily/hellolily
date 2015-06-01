import django_filters
from rest_framework import viewsets, mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import list_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .serializers import LilyGroupSerializer, LilyUserSerializer, LilyUserTokenSerializer
from ..models import LilyGroup, LilyUser


class TeamFilter(django_filters.FilterSet):
    """
    Class to filter case queryset.
    """

    class Meta:
        model = LilyGroup
        fields = ['name', ]


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all teams assigned to the current user.
    """
    model = LilyGroup
    serializer_class = LilyGroupSerializer
    filter_class = TeamFilter
    queryset = LilyGroup.objects

    def get_queryset(self):
        queryset = self.model.objects.filter(tenant_id=self.request.user.tenant_id)
        return queryset

    def get(self, request, format=None):
        filtered_queryset = self.filter_class(request.GET, queryset=self.get_queryset())
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'])
    def mine(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user=self.request.user)
        filtered_queryset = self.filter_class(request.GET, queryset=queryset)
        serializer = self.serializer_class(filtered_queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class LilyUserViewSet(mixins.UpdateModelMixin,
                      viewsets.ReadOnlyModelViewSet):

    model = LilyUser
    serializer_class = LilyUserSerializer
    queryset = LilyUser.objects

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

    @list_route(methods=['GET', 'DELETE', 'POST'])
    def token(self, request, *args, **kwargs):
        """
        This view only returns the token of the currently logged in user

        GET returns the current token
        POST generates a new token
        DELETE removes the current token
        """
        if request.method in ('DELETE', 'POST'):
            Token.objects.filter(user=request.user).delete()
            if request.method == 'DELETE':
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                Token.objects.create(user=request.user)

        serializer = LilyUserTokenSerializer(request.user)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if self.request.user != self.get_object():
            raise PermissionDenied

        return super(LilyUserViewSet, self).update(request, args, kwargs)

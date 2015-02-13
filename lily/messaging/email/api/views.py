from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import EmailLabelSerializer, EmailAccountSerializer, EmailMessageSerializer
from ..models import EmailLabel, EmailAccount, EmailMessage
from ..tasks import trash_email_message, delete_email_message, archive_email_message, toggle_read_email_message


class EmailLabelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLabel.objects.all()
    serializer_class = EmailLabelSerializer
    filter_fields = ('account__id', 'label_id')

    def get_queryset(self):
        return EmailLabel.objects.filter(account__tenant_id=self.request.user.tenant_id)


class EmailAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLabel.objects.all()
    serializer_class = EmailAccountSerializer

    def get_queryset(self):
        return EmailAccount.objects.filter(
            Q(owner=self.request.user) |
            Q(public=True) |
            Q(shared_with_users__id=self.request.user.pk)
        )


class EmailMessageViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):

    queryset = EmailMessage.objects.all()
    serializer_class = EmailMessageSerializer

    def get_queryset(self):
        return EmailMessage.objects.filter(account__tenant=self.request.user.tenant)

    def perform_update(self, serializer):
        """
        Any modifications are passed trough the manager and not directly on de db.

        For now, only the read status will be updated.
        """
        email = self.get_object()
        toggle_read_email_message.apply_async(args=(email.id, self.request.data['read']))

    def perform_destroy(self, instance):
        """
        Any modifications are passed trough the manager and not directly on de db.

        Delete will happen async
        """
        delete_email_message.apply_async(args=(instance.id,))

    @detail_route(methods=['put'])
    def archive(self, request, pk=None):
        """
        Any modifications are passed trough the manager and not directly on de db.

        Archive will happen async
        """
        email = self.get_object()
        serializer = self.get_serializer(email, partial=True)
        archive_email_message.apply_async(args=(email.id,))
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def trash(self, request, pk=None):
        """
        Any modifications are passed trough the manager and not directly on de db.

        Trash will happen async
        """
        email = self.get_object()
        serializer = self.get_serializer(email, partial=True)
        trash_email_message.apply_async(args=(email.id,))
        return Response(serializer.data)

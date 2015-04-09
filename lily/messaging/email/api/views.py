from django.db.models import Q
from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from lily.users.models import LilyUser

from .serializers import EmailLabelSerializer, EmailAccountSerializer, EmailMessageSerializer, EmailTemplateSerializer
from ..models.models import EmailLabel, EmailAccount, EmailMessage, EmailTemplate
from ..tasks import (trash_email_message, delete_email_message, archive_email_message, toggle_read_email_message,
                     add_and_remove_labels_for_message)


class EmailLabelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLabel.objects.all()
    serializer_class = EmailLabelSerializer
    filter_fields = ('account__id', 'label_id')

    def get_queryset(self):
        return EmailLabel.objects.filter(account__tenant_id=self.request.user.tenant_id)


class EmailAccountViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.ReadOnlyModelViewSet):

    queryset = EmailLabel.objects.all()
    serializer_class = EmailAccountSerializer
    filter_fields = (
        'owner',
        'shared_with_users__id',
        'public',
    )

    def get_queryset(self):
        return EmailAccount.objects.filter(
            Q(owner=self.request.user) |
            Q(public=True) |
            Q(shared_with_users__id=self.request.user.pk)
        ).filter(is_deleted=False).distinct('id')

    def perform_destroy(self, instance):
        if instance.owner_id is self.request.user.id:
            instance.is_deleted = True
            instance.save()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @detail_route(methods=['post'])
    def shared(self, request, pk):
        """
        shared action makes it possible for the owner of the emailaccount to POST user ids to share emailaccount with.

        Accepts POST dict with:
            {
                'shared_with_users': [<list of user ids as ints]
            }

        Returns:
            changed EmailAccount
        """
        account = EmailAccount.objects.get(id=pk, owner=request.user)
        account.shared_with_users.clear()
        account.public = False
        account.save()

        for user_id in request.data['shared_with_users']:
            user = LilyUser.objects.get(id=user_id, tenant=request.user.tenant)
            account.shared_with_users.add(user)

        serializer = self.get_serializer(account)

        return Response(serializer.data)


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

    @detail_route(methods=['put'])
    def move(self, request, pk=None):
        """
        Any modifications are passed trough the manager and not directly on de db.

        Move will happen async
        """
        email = self.get_object()
        serializer = self.get_serializer(email, partial=True)
        add_and_remove_labels_for_message.delay(
            email.id,
            remove_labels=request.data['data'].get('remove_labels', []),
            add_labels=request.data['data'].get('add_labels', []),
        )
        return Response(serializer.data)


class EmailTemplateViewSet(mixins.DestroyModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    """
    EmailTemplate API.
    """
    queryset = EmailTemplate.objects
    serializer_class = EmailTemplateSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('name', )

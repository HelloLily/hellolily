import logging

from django.conf import settings
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import phonenumbers
from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from lily.accounts.models import Account
from lily.messaging.email.utils import get_email_parameter_api_dict, reindex_email_message, get_shared_email_accounts
from lily.search.lily_search import LilySearch
from lily.users.models import UserInfo
from lily.users.api.serializers import LilyUserSerializer

from .serializers import (EmailLabelSerializer, EmailAccountSerializer, EmailMessageSerializer,
                          EmailTemplateFolderSerializer, EmailTemplateSerializer, SharedEmailConfigSerializer,
                          TemplateVariableSerializer)
from ..models.models import (EmailLabel, EmailAccount, EmailMessage, EmailTemplateFolder, EmailTemplate,
                             SharedEmailConfig, TemplateVariable)
from ..tasks import (trash_email_message, toggle_read_email_message,
                     add_and_remove_labels_for_message, toggle_star_email_message, toggle_spam_email_message)
from ..utils import get_filtered_message


logger = logging.getLogger(__name__)


class EmailLabelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLabel.objects.all()
    serializer_class = EmailLabelSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('account__id', 'label_id')

    def get_queryset(self):
        return EmailLabel.objects.filter(account__tenant_id=self.request.user.tenant_id)


class SharedEmailConfigViewSet(viewsets.ModelViewSet):
    queryset = SharedEmailConfig.objects.all()
    serializer_class = SharedEmailConfigSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (DjangoFilterBackend,)
    filter_fields = {
        'email_account',
        'is_hidden',
    }

    def perform_create(self, serializer):
        email_account_id = self.request.data['email_account']
        try:
            shared_email_setting = self.get_queryset().get(email_account_id=email_account_id)
        except SharedEmailConfig.DoesNotExist:
            serializer.save(tenant_id=self.request.user.tenant_id, user=self.request.user)
        else:
            if 'is_hidden' in self.request.data:
                shared_email_setting.is_hidden = self.request.data.get('is_hidden')
                shared_email_setting.save()

    def perform_update(self, serializer):
        if 'is_hidden' in self.request.data:
            is_hidden = self.request.data.get('is_hidden')

        serializer.save(tenant_id=self.request.user.tenant_id, user=self.request.user, is_hidden=is_hidden)

    def get_queryset(self):
        return SharedEmailConfig.objects.filter(tenant_id=self.request.user.tenant_id,
                                                user=self.request.user)


class EmailAccountViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.ReadOnlyModelViewSet):

    queryset = EmailAccount.objects.all()
    serializer_class = EmailAccountSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (DjangoFilterBackend,)
    filter_fields = (
        'owner',
        'sharedemailconfig__user__id',
        'privacy',
    )

    def get_queryset(self):
        return EmailAccount.objects.filter(is_deleted=False).distinct('id')

    def perform_destroy(self, instance):
        if instance.owner_id == self.request.user.id:
            instance.delete()
            instance.is_authorized = False
            instance.sharedemailconfig_set.all().delete()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @list_route()
    def mine(self, request):
        email_account_list = get_shared_email_accounts(request.user)

        serializer = self.get_serializer(email_account_list, many=True)

        return Response(serializer.data)

    @detail_route(methods=['delete'])
    def cancel(self, request, pk):
        """
        Cancel creation of an email account and deletes it.

        Returns:

        """
        user = request.user
        account = EmailAccount.objects.get(id=pk, owner=user)

        if not account.is_authorized:
            # Account is being added, so delete it.
            account.delete()

        if not user.info.email_account_status:
            # First time setup, so set status to skipped.
            user.info.email_account_status = UserInfo.SKIPPED
            user.info.save()

            serializer = LilyUserSerializer(user, partial=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailMessageViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):

    queryset = EmailMessage.objects.all()
    serializer_class = EmailMessageSerializer

    def get_object(self):
        pk = int(self.kwargs['pk'])
        email_message = EmailMessage.objects.get(pk=pk)
        user = self.request.user

        try:
            email_account = EmailAccount.objects.get(pk=email_message.account.id)
        except EmailAccount.DoesNotExist:
            email_message = None
        else:
            email_message = get_filtered_message(email_message, email_account, user)

        if not email_message:
            raise NotFound()

        if not isinstance(email_message, EmailMessage) and self.action != 'retrieve':
            raise NotFound()

        return email_message

    def get_queryset(self):
        user = self.request.user
        email_messages = EmailMessage.objects.filter(account__tenant=user.tenant)

        # Get all email accounts.
        email_accounts = EmailAccount.objects.filter(tenant=user.tenant, is_deleted=False).distinct('id')

        filtered_queryset = []

        for email_message in email_messages:
            email_account = email_accounts.get(pk=email_message.account.id)

            filtered_message = get_filtered_message(email_message, email_account, user)

            if filtered_message:
                filtered_queryset.append(filtered_message)

        return filtered_queryset

    def perform_update(self, serializer):
        """
        For now, only the read status will be updated. Opposite to others email modification (archive, spam, star, etc)
        read status is a model field. This enables calculations of the unread count per label. So in this case
        update database directly. Save will trigger an update of the search index.
        """
        email = self.get_object()
        email.read = self.request.data['read']
        email.save()
        toggle_read_email_message.apply_async(args=(email.id, self.request.data['read']))

    def perform_destroy(self, instance):
        """
        Delete an email message asynchronous through the manager and not directly on the database.
        """
        trash_email_message.apply_async(args=(instance.id,))

    @detail_route(methods=['put'])
    def archive(self, request, pk=None):
        """
        Archive an email message asynchronous through the manager and not directly on the database. Just update the
        search index by an instance variable so changes are immediately visible.
        An email message is archived by removing the inbox label and the provided label of the current inbox.
        """
        email = self.get_object()

        current_inbox = request.data['data'].get('current_inbox', '')

        # Filter out labels an user should not manipulate.
        remove_labels = []
        if current_inbox and current_inbox not in settings.GMAIL_LABELS_DONT_MANIPULATE:
            remove_labels.append(current_inbox)

        # Archiving email should always remove the inbox label.
        if settings.GMAIL_LABEL_INBOX not in remove_labels:
            remove_labels.append(settings.GMAIL_LABEL_INBOX)

        email._is_archived = True
        reindex_email_message(email)
        serializer = self.get_serializer(email, partial=True)
        add_and_remove_labels_for_message.delay(email.id, remove_labels=remove_labels)
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def trash(self, request, pk=None):
        """
        Trash an email message asynchronous through the manager and not directly on the database. Just update the
        search index by an instance variable so changes are immediately visible.
        """
        email = self.get_object()
        if email.is_trashed:
            email._is_deleted = True
        email._is_trashed = True
        reindex_email_message(email)
        serializer = self.get_serializer(email, partial=True)
        trash_email_message.apply_async(args=(email.id,))
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def move(self, request, pk=None):
        """
        Move an email message asynchronous through the manager and not directly on the database. Just update the
        search index by an instance variable so changes are immediately visible.
        """
        email = self.get_object()
        serializer = self.get_serializer(email, partial=True)
        add_and_remove_labels_for_message.delay(
            email.id,
            add_labels=request.data['data'].get('add_labels', []),
            remove_labels=request.data['data'].get('remove_labels', []),
        )
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def star(self, request, pk=None):
        """
        Star an email message asynchronous through the manager and not directly on the database. Just update the
        search index by an instance variable so changes are immediately visible.
        """
        email = self.get_object()
        email._is_starred = request.data['starred']
        reindex_email_message(email)
        serializer = self.get_serializer(email, partial=True)
        toggle_star_email_message.delay(email.id, star=request.data['starred'])
        return Response(serializer.data)

    @detail_route(methods=['put'])
    def spam(self, request, pk=None):
        """
        Mark / unmark an email message as spam asynchronous through the manager and not directly on the database. Just
        update the search index by an instance variable so changes are immediately visible.
        """
        email = self.get_object()
        email._is_spam = request.data['markAsSpam']
        reindex_email_message(email)
        serializer = self.get_serializer(email, partial=True)
        toggle_spam_email_message.delay(email.id, spam=request.data['markAsSpam'])
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        """
        Returns what happened to an email; did the user reply or forwarded the email message.
        """
        email = self.get_object()

        account_email = email.account.email_address
        sent_from_account = (account_email == email.sender.email_address)

        # Get the messages in the thread for the current email message.
        search = LilySearch(
            request.user.tenant_id,
            model_type='email_emailmessage',
            sort='sent_date',
            size=100  # Paged results, when a thread is containing more that 100 results StopIteration could be thrown.
        )
        search.filter_query('thread_id:%s' % email.thread_id)
        thread, facets, total, took = search.do_search([
            'message_id',
            'received_by_email',
            'received_by_cc_email',
            'sender_email',
            'sender_name',
            'sent_date',
        ])

        try:
            # Get the index of the current email message in the thread.
            index = (key for key, item in enumerate(thread) if item['message_id'] == email.message_id).next()
        except StopIteration:
            logger.exception('Number of messages larger that search page size for message %s.' % email.id)
            results = {}
            return Response(results)

        # Only look at the messages in the thread after the current email message.
        messages_after = thread[index + 1:]

        results = {}

        if not messages_after or sent_from_account:
            # Current email message is the last in the thread or is send by the user and therefor not a possible reply
            # or forwarded email message.
            return Response(results)

        # The current email message isn't the last in the thread. So look the follow up messages in the thread to
        # determine what actions occured on the current email message. Current email message is not send from the
        # account of the user, so it is a received email message. So determine is we replied or forwarded it.

        # Get all the outgoing follow up messages in the thread.
        next_messages = [item for item in messages_after if item['sender_email'] == account_email]
        if len(next_messages):
            # We only need to look at the first follow up message in the thread.
            # TODO LILY-2244: improve search filter above so it leads to the only / first follow up message.
            next_message = next_messages[0]

            # Get all the mail addresses where the follow up message was sent to.
            email_addresses = next_message.get('received_by_email', []) + next_message.get('received_by_cc_email', [])

            if email_addresses.count(email.sender.email_address):
                # The sender of the current, received email message is one of the reciepents of the follow up message,
                # so it is a reply message.
                results['replied_with'] = next_message
            else:
                results['forwarded_with'] = next_message

        return Response(results)

    @detail_route(methods=['post'])
    def extract(self, request, pk=None):
        """
        Attempt to extract phone numbers from the given email message. If account is given it will
        """
        email = self.get_object()
        account = request.data['account']
        country = None

        if account:
            account = Account.objects.get(pk=account)

            if account.addresses:
                address = account.addresses.first()

                if address:
                    country = address.country

        if not country:
            country = self.request.user.tenant.country or None

        phone_numbers = []

        # We can't extract phone numbers without a country.
        if country:
            for match in phonenumbers.PhoneNumberMatcher(email.body_text, country):
                number_format = phonenumbers.PhoneNumberFormat.NATIONAL
                number = match.number

                number = phonenumbers.format_number(number, number_format).replace(' ', '')

                if number not in phone_numbers:
                    phone_numbers.append(number)

        return Response({'phone_numbers': phone_numbers})


class EmailTemplateFolderViewSet(viewsets.ModelViewSet):
    """
    EmailTemplateFolder API.
    """
    # Set the queryset, this takes care of setting the `base_name`.
    queryset = EmailTemplateFolder.objects
    # Set the serializer class for this viewset.
    serializer_class = EmailTemplateFolderSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (filters.OrderingFilter, )

    # OrderingFilter: set the default ordering fields.
    ordering = ('name', )

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant.
        """
        folders = super(EmailTemplateFolderViewSet, self).get_queryset().all()

        for folder in folders:
            folder.email_templates = folder.email_templates.order_by('name')

        return folders

    def destroy(self, request, *args, **kwargs):
        """
        Unlink all email templates from the folder and then delete the folder.
        """
        folder = self.get_object()

        templates = folder.email_templates.all()

        for template in templates:
            template.folder = None
            template.save()

        # Don't call super, since that only fires another query using self.get_object().
        self.perform_destroy(folder)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailTemplateFilter(FilterSet):
    class Meta:
        model = EmailTemplate
        fields = {
            'folder': ['isnull', ],
        }


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    EmailTemplate API.
    """
    # Set the queryset, this takes care of setting the `base_name`.
    queryset = EmailTemplate.objects
    # Set the serializer class for this viewset.
    serializer_class = EmailTemplateSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (filters.OrderingFilter, filters.DjangoFilterBackend)

    filter_class = EmailTemplateFilter

    # OrderingFilter: set the default ordering fields.
    ordering = ('name', )

    def get_queryset(self):
        """
        Set the queryset here so it filters on tenant.
        """
        return super(EmailTemplateViewSet, self).get_queryset().all()

    @list_route(methods=['PATCH'])
    def move(self, request):
        templates = request.data.get('templates')
        folder = request.data.get('folder')

        if folder:
            folder = EmailTemplateFolder.objects.get(pk=folder)

        templates = EmailTemplate.objects.filter(id__in=templates)

        for template in templates:
            template.folder = folder
            template.save()

        return Response(status=status.HTTP_200_OK)


class TemplateVariableViewSet(mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              GenericViewSet):
    """
    TemplateVariable API.
    """
    queryset = TemplateVariable.objects
    serializer_class = TemplateVariableSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('name', )

    def list(self, request):
        queryset = TemplateVariable.objects.all().filter(Q(is_public=True) | Q(owner=request.user))
        serializer = TemplateVariableSerializer(queryset, many=True)

        default_variables = get_email_parameter_api_dict()

        template_variables = {
            'default': default_variables,
            'custom': serializer.data
        }

        return Response(template_variables)

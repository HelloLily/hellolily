import logging

from django.apps import apps
from ddtrace import tracer
from django.conf import settings
from django.db.models import Q
from django_filters import rest_framework as filters
import phonenumbers
from oauth2client.client import HttpAccessTokenRefreshError
from rest_framework import viewsets, mixins, status
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from lily.accounts.models import Account
from lily.messaging.email.utils import get_shared_email_accounts, reindex_email_message
from lily.messaging.email.connector import GmailConnector, NotFoundError, FailedServiceCallException
from lily.messaging.email.credentials import InvalidCredentialsError
from lily.messaging.email.tasks import send_message
from lily.utils.functions import format_phone_number
from lily.utils.models.models import PhoneNumber

from .serializers import (EmailLabelSerializer, EmailAccountSerializer, EmailMessageSerializer,
                          EmailTemplateFolderSerializer, EmailTemplateSerializer, SharedEmailConfigSerializer,
                          TemplateVariableSerializer, EmailAttachmentSerializer, EmailDraftCreateSerializer,
                          EmailDraftReadSerializer, EmailDraftUpdateSerializer, EmailDraftAttachmentReadSerializer,
                          SimpleEmailAccountSerializer, EmailMessageListSerializer,
                          EmailDraftAttachmentCreateSerializer)
from ..models.models import (EmailLabel, EmailAccount, EmailMessage, EmailTemplateFolder, EmailTemplate,
                             SharedEmailConfig, TemplateVariable, EmailDraft, EmailDraftAttachment)
from ..tasks import (trash_email_message, toggle_read_email_message, add_and_remove_labels_for_message,
                     toggle_star_email_message, toggle_spam_email_message)
from ..utils import get_filtered_message, determine_message_type


logger = logging.getLogger(__name__)


class EmailLabelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLabel.objects.all()
    serializer_class = EmailLabelSerializer

    # Set all filter backends that this viewset uses.
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('account__id', 'label_id')
    swagger_schema = None

    def get_queryset(self):
        return EmailLabel.objects.filter(account__tenant_id=self.request.user.tenant_id)


class SharedEmailConfigViewSet(viewsets.ModelViewSet):
    queryset = SharedEmailConfig.objects.all()
    serializer_class = SharedEmailConfigSerializer
    swagger_schema = None

    # Set all filter backends that this viewset uses.
    filter_backends = (filters.DjangoFilterBackend,)
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
    swagger_schema = None

    # Set all filter backends that this viewset uses.
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = (
        'owner',
        'sharedemailconfig__user__id',
        'privacy',
    )

    def get_queryset(self):
        email_account_list = EmailAccount.objects.filter(is_deleted=False).distinct('id')
        email_account_list = email_account_list.prefetch_related(
            'labels',
            'sharedemailconfig_set',
        )

        return email_account_list

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
        email_account_list = email_account_list.prefetch_related(
            'labels',
            'sharedemailconfig_set',
            'owner',
        )
        serializer = self.get_serializer(email_account_list, many=True)

        return Response({'results': serializer.data})

    @list_route()
    def color(self, request):
        email_account_list = get_shared_email_accounts(request.user)
        serializer = SimpleEmailAccountSerializer(email_account_list, many=True)
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

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailMessageViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    queryset = EmailMessage.objects.all()
    serializer_class = EmailMessageSerializer
    swagger_schema = None

    def get_object(self, pk=None):
        if not pk:
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

    @detail_route(methods=['put', 'patch'])
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

    @detail_route(methods=['put', 'patch'])
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

    @detail_route(methods=['put', 'patch'])
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

    @detail_route(methods=['put', 'patch'])
    def spam(self, request, pk=None):
        """
        Mark / unmark an email message as spam asynchronous through the manager and not directly on the database. Just
        update the search index by an instance variable so changes are immediately visible.
        """
        email = self.get_object()
        email._is_spam = request.data['markAsSpam']
        serializer = self.get_serializer(email, partial=True)
        toggle_spam_email_message.delay(email.id, spam=request.data['markAsSpam'])
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def history(self, request, pk):
        """
        Returns what happened to an email; did the user reply or forwarded the email message.
        """
        message = self.get_object()
        message_type, message_type_to_id = determine_message_type(
            message.thread_id,
            message.sent_date,
            message.account.email_address
        )

        data = dict(action='nothing')
        if message_type_to_id:
            if not self.get_object(message_type_to_id):
                return Response({})

            data['action_message_id'] = message_type_to_id

            if message_type == EmailMessage.REPLY:
                data['action'] = 'reply'
            elif message_type == EmailMessage.REPLY_ALL:
                data['action'] = 'reply-all'
            elif message_type == EmailMessage.FORWARD:
                data['action'] = 'forward'
            elif message_type == EmailMessage.FORWARD_MULTI:
                data['action'] = 'forward-multi'

        return Response(data)

    @detail_route(methods=['post'])
    def extract(self, request, pk=None):
        """
        Attempt to extract phone numbers from the given email message.
        If an account is given it will attempt to use that account's country.
        Otherwise it will use the user's tenant's country.
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
                number = format_phone_number(number, country, True)

                number_exists = PhoneNumber.objects.filter(number=number, status=PhoneNumber.ACTIVE_STATUS).exists()

                if number not in phone_numbers and not number_exists:
                    phone_numbers.append(number)

        return Response({'phone_numbers': phone_numbers})

    @detail_route(methods=['GET'])
    def attachments(self, request, pk=None):
        """
        Mark / unmark an email message as spam asynchronous through the manager and not directly on the database. Just
        update the search index by an instance variable so changes are immediately visible.
        """
        email = self.get_object()

        attachments = email.attachments.all()
        serializer = EmailAttachmentSerializer(attachments, many=True)

        return Response({'results': serializer.data})

    @detail_route(methods=['GET'])
    def thread(self, request, pk):
        email = self.get_object()
        messages = EmailMessage.objects.filter(thread_id=email.thread_id).order_by('sent_date')
        serializer = EmailMessageSerializer(messages, many=True)

        return Response({'results': serializer.data})


class EmailTemplateFolderViewSet(viewsets.ModelViewSet):
    """
    EmailTemplateFolder API.
    """
    # Set the queryset, this takes care of setting the `base_name`.
    queryset = EmailTemplateFolder.objects
    # Set the serializer class for this viewset.
    serializer_class = EmailTemplateFolderSerializer
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter, )
    swagger_schema = None

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


class EmailTemplateFilter(filters.FilterSet):
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
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    filter_class = EmailTemplateFilter
    swagger_schema = None

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

        return Response(status=status.HTTP_204_NO_CONTENT)


class TemplateVariableViewSet(mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              GenericViewSet):
    """
    TemplateVariable API.
    """
    queryset = TemplateVariable.objects
    serializer_class = TemplateVariableSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('name', )
    swagger_schema = None

    def list(self, request):
        queryset = TemplateVariable.objects.all().filter(Q(is_public=True) | Q(owner=request.user))
        serializer = TemplateVariableSerializer(queryset, many=True)

        default_variables = {}

        for model in apps.get_models():
            if hasattr(model, 'EMAIL_TEMPLATE_PARAMETERS'):
                for field in model.EMAIL_TEMPLATE_PARAMETERS:
                    default_variables.setdefault(model._meta.verbose_name.lower(), []).append(field)

        template_variables = {
            'default': default_variables,
            'custom': serializer.data
        }

        return Response(template_variables)


class EmailDraftViewSet(viewsets.ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes
    # care of setting the `base_name`.
    queryset = EmailDraft.objects
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter,)
    ordering_fields = ('id',)
    ordering = ('id',)

    def initial(self, request, *args, **kwargs):
        """ Anything that should happen after permission checks and before dispatching. """
        super(EmailDraftViewSet, self).initial(request, *args, **kwargs)

        # Store the email accounts on the class so we only have to fetch them once.
        self.available_accounts = get_shared_email_accounts(self.request.user)

    def get_queryset(self):
        return super(EmailDraftViewSet, self).get_queryset().filter(
            send_from__in=self.available_accounts
        ).order_by('id')

    def get_serializer_class(self):
        method_serializer_classes = {
            ('POST', ): EmailDraftCreateSerializer,
            ('GET', ): EmailDraftReadSerializer,
            ('PUT', 'PATCH', ): EmailDraftUpdateSerializer
        }

        for methods, serializer_cls in method_serializer_classes.items():
            if self.request.method in methods:
                return serializer_cls

    def get_serializer_context(self):
        context = super(EmailDraftViewSet, self).get_serializer_context()

        # We give the available email accounts to the serializer to prevent extra queries to fetch them again.
        context['available_accounts'] = self.available_accounts

        return context

    @detail_route(methods=['post'])
    def send(self, request, pk=None):
        draft = self.get_object()

        send_message.delay(draft.id, draft=True)

        return Response({'status': 'Email is being sent'})


class SearchView(APIView):
    """
    Search for email messages by using the Gmail Search API. Our search therefor provides the same operators Gmail
    offers: https://support.google.com/mail/answer/7190

    The Gmail API returns message_id's for the messages that are the result of the search query. Using those
    messages_id's the corresponding email messages are subsequently retrieved from our database.
    """

    def get(self, request, format=None):
        with tracer.trace('SearchView.get: parameter setup'):
            user = request.user

            # Search query.
            q = request.query_params.get('q', '').strip()

            # Paging parameters.
            page = request.query_params.get('page', '0')
            page = int(page) + 1
            size = int(request.query_params.get('size', '20'))
            sort = request.query_params.get('sort', '-sent_date')

            # Mail labeling parameters.
            label_id = request.query_params.get('label', None)

            account_ids = request.query_params.get('account', None)  # None means search in all owned email accounts.

        with tracer.trace('SearchView.get: email_accounts setup'):
            # Get a list of all email accounts added by the user or publicly shared with the user as a group inbox.
            email_accounts = get_shared_email_accounts(user, True)

            if account_ids:
                # Only search within the email accounts indicated by the account_ids parameter.
                account_ids = account_ids.split(',')
                email_accounts = email_accounts.filter(pk__in=account_ids)

            email_accounts = email_accounts.exclude(
                Q(is_active=False) |
                Q(is_deleted=True) |
                Q(is_authorized=False)
            )

        message_list = EmailMessage.objects

        if q:
            # System Gmail labels visible in Lily, where the user can search in.
            gmail_labels = [
                settings.GMAIL_LABEL_INBOX,
                settings.GMAIL_LABEL_SPAM,
                settings.GMAIL_LABEL_TRASH,
                settings.GMAIL_LABEL_SENT,
                settings.GMAIL_LABEL_DRAFT
            ]

            if label_id and label_id not in gmail_labels:
                # Also retrieve related user set labels because later the label name will be queried.
                email_accounts = email_accounts.prefetch_related('labels')

            # Prevent too much calls on the search api, so restrict number of search results per email account.
            max_results = 3 * size

            messages_ids = []

            with tracer.trace('SearchView.get: for all accounts'):
                for email_account in email_accounts:
                    if label_id:
                        with tracer.trace('SearchView.get: building q with label lookup'):
                            # Retrieve the label corresponding to the label_id, otherwise Gmail defaults to all mail.
                            label_name = label_id
                            if label_id not in gmail_labels:
                                # Retrieve the label name if label_id will differ from the user set label name.
                                try:
                                    label_name = email_account.labels.get(label_id=label_id).name
                                except EmailLabel.DoesNotExist:
                                    logger.error(
                                        "Incorrect label id {0} with search request for account {1}.".format(
                                            label_id,
                                            email_account
                                        )
                                    )
                                    # Failing label lookup within one account should not halt the complete search.
                                    continue

                            q = u"{0} {1}:{2}".format(q, 'label', label_name)

                    with tracer.trace('SearchView.get: retrieving message_ids by Gmail API'):
                        try:
                            connector = GmailConnector(email_account)
                            messages = connector.search(query=q, size=max_results)
                            messages_ids.extend([message['id'] for message in messages])
                        except (InvalidCredentialsError, NotFoundError, HttpAccessTokenRefreshError,
                                FailedServiceCallException) as e:
                            logger.error(
                                "Failed to search within account {0} with error: {1}.".format(email_account, e)
                            )
                            # Failing search within one account should not halt the complete search.
                            continue

                # Retrieve messages from the database.
                message_list = message_list.filter(
                    message_id__in=messages_ids,
                    account__in=email_accounts
                )

        with tracer.trace('SearchView.get: retrieving messages from db'):
            message_list = message_list.order_by(sort)

            # Exclude fields that aren't serialized and potential large.
            message_list = message_list.defer("body_html", "body_text", "snippet")

            # The serializer will query for account, sender and star label, so instead of the extra separate queries,
            # retrieve them now.
            message_list = message_list.select_related('account', 'sender')
            message_list = message_list.prefetch_related('labels', 'received_by')

            # It's possible Google search returns message_id's that aren't in the database (due to 'sync from now').
            actual_number_of_results = len(message_list)

        with tracer.trace('SearchView.get: serializing messages'):
            # Construct paginator.
            limit = size * page
            offset = limit - size
            message_list = message_list[offset:limit]

            serializer = EmailMessageListSerializer(message_list, many=True)

            result = {
                'hits': serializer.data,
                'total': actual_number_of_results,
            }

        return Response(result)


class EmailDraftAttachmentViewSet(viewsets.ModelViewSet):
    # Set the queryset, without .all() this filters on the tenant and takes
    # care of setting the `base_name`.
    queryset = EmailDraftAttachment.objects
    # Set all filter backends that this viewset uses.
    filter_backends = (OrderingFilter,)
    ordering_fields = ('id',)
    ordering = ('id',)
    serializer_class = EmailDraftAttachmentReadSerializer

    def initial(self, request, *args, **kwargs):
        """ Anything that should happen after permission checks and before dispatching. """
        super(EmailDraftAttachmentViewSet, self).initial(request, *args, **kwargs)

        # Store the email accounts on the class so we only have to fetch them once.
        self.available_accounts = get_shared_email_accounts(self.request.user)

        try:
            self.draft = EmailDraft.objects.get(
                pk=kwargs['draft_id'],
                send_from__in=self.available_accounts
            )
        except EmailDraft.DoesNotExist:
            raise NotFound()

    def get_queryset(self):
        return super(EmailDraftAttachmentViewSet, self).get_queryset().filter(
            email_draft=self.draft,
            email_draft__send_from__in=self.available_accounts
        ).order_by('id')

    def get_serializer_class(self):
        method_serializer_classes = {
            ('GET', ): EmailDraftAttachmentReadSerializer,
            ('POST', ): EmailDraftAttachmentCreateSerializer,
        }

        for methods, serializer_cls in method_serializer_classes.items():
            if self.request.method in methods:
                return serializer_cls

    def get_serializer_context(self):
        context = super(EmailDraftAttachmentViewSet, self).get_serializer_context()

        # We give the available email accounts to the serializer to prevent extra queries to fetch them again.
        context['available_accounts'] = self.available_accounts
        context['draft'] = self.draft

        return context

from itertools import chain
import anyjson
import HTMLParser
import logging
import mimetypes
import re
import urllib

from braces.views import StaticContextMixin
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
from celery.states import FAILURE
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import default_storage
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404, HttpResponse
from django.template import Context, Template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView, DeleteView, CreateView, FormView
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from googleapiclient.errors import HttpError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.django_orm import Storage

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.google.token_generator import generate_token, validate_token
from lily.integrations.credentials import get_credentials
from lily.tenant.middleware import get_current_user
from lily.users.models import UserInfo
from lily.utils.functions import is_ajax, post_intercom_event, send_get_request, send_post_request
from lily.utils.views.mixins import LoginRequiredMixin, FormActionMixin

from .forms import (ComposeEmailForm, CreateUpdateEmailTemplateForm, CreateUpdateTemplateVariableForm,
                    EmailAccountCreateUpdateForm, EmailTemplateFileForm)
from .models.models import (EmailMessage, EmailAttachment, EmailAccount, EmailTemplate, DefaultEmailTemplate,
                            EmailOutboxMessage, EmailOutboxAttachment, TemplateVariable, GmailCredentialsModel,
                            EmailLabel)
from .services import GmailService
from .tasks import (send_message, create_draft_email_message, update_draft_email_message,
                    add_and_remove_labels_for_message, trash_email_message)
from .utils import (get_attachment_filename_from_url, get_email_parameter_choices, create_recipients,
                    render_email_body, replace_cid_in_html, create_reply_body_header, reindex_email_message,
                    extract_script_tags)


logger = logging.getLogger(__name__)


FLOW = OAuth2WebServerFlow(
    client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
    redirect_uri=settings.GMAIL_CALLBACK_URL,
    scope='https://mail.google.com/',
    prompt='consent',
    access_type='offline',
)


class SetupEmailAuth(LoginRequiredMixin, View):
    def get(self, request):
        state = b64encode(anyjson.serialize({
            'token': generate_token(settings.SECRET_KEY, request.user.pk),
        }))
        authorize_url = FLOW.step1_get_authorize_url(state=state)

        return HttpResponseRedirect(authorize_url)


class OAuth2Callback(LoginRequiredMixin, View):
    def get(self, request):
        error = request.GET.get('error')
        if error:
            messages.error(
                self.request,
                _('Sorry, Lily needs authorization from Google to synchronize your email account.')
            )
            return HttpResponseRedirect('/#/preferences/emailaccounts')

        # Get the state param from the request.
        state = str(request.GET.get('state'))
        # Replace %xx characters with single quotes and UTF8 decode the string.
        state = urllib.unquote(state).decode('utf8')
        # Deserialize the JSON string.
        state = anyjson.deserialize(b64decode(state))

        if not validate_token(settings.SECRET_KEY, state.get('token'), request.user.pk):
            return HttpResponseBadRequest()

        credentials = FLOW.step2_exchange(code=request.GET.get('code'))

        # Setup service to retrieve email address from Google.
        gmail_service = GmailService(credentials)
        try:
            profile = gmail_service.execute_service(gmail_service.service.users().getProfile(userId='me'))
        except HttpError as error:
            error = anyjson.loads(error.content)
            error = error.get('error', error)
            if error.get('code') == 400 and error.get('message') == 'Mail service not enabled':
                messages.error(self.request, _('Mail is not enabled for this email account.'))
            else:
                messages.error(self.request, error.get('message'))

            # Adding email account failed, administer it as skipping the email setup or otherwise the user will be
            # stuck in redirect loop.
            user = self.request.user
            user.info.email_account_status = UserInfo.SKIPPED
            user.info.save()

            return HttpResponseRedirect('/#/preferences/emailaccounts')

        # Create account based on email address.
        try:
            account, created = EmailAccount.objects.get_or_create(
                owner=request.user,
                tenant_id=request.user.tenant_id,
                email_address=profile.get('emailAddress')
            )
        except EmailAccount.MultipleObjectsReturned:
            account, created = EmailAccount.objects.get_or_create(
                owner=request.user,
                tenant_id=request.user.tenant_id,
                email_address=profile.get('emailAddress'),
                is_deleted=False
            )

        # Store credentials based on new email account.
        storage = Storage(GmailCredentialsModel, 'id', account, 'credentials')
        storage.put(credentials)

        account.is_deleted = False

        if created:
            account.only_new = None

        account.save()

        post_intercom_event(event_name='email-account-added', user_id=request.user.id)

        if request.user.info and not request.user.info.email_account_status:
            # First time setup, so we want a different view.
            return HttpResponseRedirect('/#/preferences/emailaccounts/setup/%s' % account.pk)
        else:
            return HttpResponseRedirect('/#/preferences/emailaccounts/edit/%s' % account.pk)


class EmailAccountUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormActionMixin, StaticContextMixin, UpdateView):
    template_name = 'email/emailaccount_form.html'
    model = EmailAccount
    form_class = EmailAccountCreateUpdateForm
    success_message = _('%(label)s has been updated.')
    static_context = {'form_prevent_autofill': True}

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(EmailAccountUpdateView, self).get_context_data(**kwargs)
        kwargs.update({
            'back_url': self.get_success_url(),
        })

        return kwargs

    def get_object(self, queryset=None):
        """
        A user is only able to edit accounts he owns.
        """
        email_account = super(EmailAccountUpdateView, self).get_object(queryset=queryset)
        if not email_account.owner == self.request.user and not email_account.public:
            raise Http404()

        return email_account

    def get_success_url(self):
        return '/#/preferences/emailaccounts'


class EmailMessageHTMLView(LoginRequiredMixin, DetailView):
    """
    Display an email body in an isolated html.
    """
    model = EmailMessage
    template_name = 'email/emailmessage_html.html'

    def get_context_data(self, **kwargs):
        context = super(EmailMessageHTMLView, self).get_context_data(**kwargs)
        context['body_html'] = render_email_body(self.object.body_html, self.object.attachments.all(), self.request)
        return context


class EmailAttachmentProxy(View):
    def get(self, request, *args, **kwargs):
        try:
            attachment = EmailAttachment.objects.get(
                pk=self.kwargs['pk'],
                message__account__tenant_id=self.request.user.tenant.id
            )
        except:
            raise Http404()

        s3_file = default_storage._open(attachment.attachment.name)

        wrapper = FileWrapper(s3_file)
        if hasattr(s3_file, 'key'):
            content_type = s3_file.key.content_type
        else:
            content_type = mimetypes.guess_type(s3_file.file.name)[0]

        response = HttpResponse(wrapper, content_type=content_type)

        inline = 'attachment'
        if attachment.inline:
            inline = 'inline'

        response['Content-Disposition'] = '%s; filename=%s' % (inline, get_attachment_filename_from_url(s3_file.name))
        response['Content-Length'] = attachment.size
        return response


#
# EmailMessage compose views (create/edit draft, reply, forward) incl. preview & send message.
#
class EmailMessageComposeView(LoginRequiredMixin, FormView):
    template_name = 'email/emailmessage_compose.html'
    form_class = ComposeEmailForm
    object = None
    remove_old_message = True
    success_url = '#/email/all/INBOX'

    def get(self, request, *args, **kwargs):
        self.get_object(request, **kwargs)
        return super(EmailMessageComposeView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_object(request, **kwargs)
        return super(EmailMessageComposeView, self).post(request, *args, **kwargs)

    def get_object(self, request, **kwargs):
        if 'pk' in kwargs:
            try:
                self.object = EmailMessage.objects.get(
                    account__tenant=request.user.tenant,
                    id=kwargs['pk'],
                )

                attachments = EmailAttachment.objects.filter(message_id=self.object.pk)

                # Strip malicious/unwanted content when replying.
                self.object.body_html = extract_script_tags(self.object.body_html)
                self.object.body_html = replace_cid_in_html(self.object.body_html, attachments, request)
            except EmailMessage.DoesNotExist:
                pass

    def form_valid(self, form):
        """
        Process form to create an email message with attachments.

        Args:
            form

        Returns:
            email_outbox_message (instance): EmailOutboxMessage instance
        """
        email_draft = form.cleaned_data
        email_account = email_draft['send_from']
        soup = BeautifulSoup(email_draft['body_html'], 'lxml')
        mapped_attachments = soup.findAll('img', {'cid': lambda cid: cid})

        if 'tasks' not in self.request.session:
            self.request.session['tasks'] = {}

        email_outbox_message = EmailOutboxMessage.objects.create(
            subject=email_draft['subject'],
            send_from=email_account,
            to=anyjson.dumps(email_draft['send_to_normal'] if len(email_draft['send_to_normal']) else None),
            cc=anyjson.dumps(email_draft['send_to_cc'] if len(email_draft['send_to_cc']) else None),
            bcc=anyjson.dumps(email_draft['send_to_bcc'] if len(email_draft['send_to_bcc']) else None),
            body=email_draft['body_html'],
            headers=anyjson.dumps(self.get_email_headers()),
            mapped_attachments=len(mapped_attachments),
            template_attachment_ids=self.request.POST.get('template_attachment_ids'),
            original_message_id=self.kwargs.get('pk')
        )

        for attachment_form in form.cleaned_data.get('attachments'):
            if attachment_form.cleaned_data and not attachment_form.cleaned_data['DELETE']:
                form_attachment = attachment_form.cleaned_data
                if not form_attachment['id']:
                    # Uploaded file, add it to email_outbox_message.
                    outbox_attachment = EmailOutboxAttachment()
                    outbox_attachment.attachment = form_attachment['attachment']
                    outbox_attachment.content_type = form_attachment['attachment'].content_type
                    outbox_attachment.email_outbox_message = email_outbox_message
                    outbox_attachment.size = form_attachment['attachment'].size
                    outbox_attachment.save()

        # Store the ids of the original message attachments.
        original_attachment_ids = self.get_original_attachment_ids(form)
        email_outbox_message.original_attachment_ids = ','.join(original_attachment_ids)
        email_outbox_message.save()

        return email_outbox_message

    def get_original_attachment_ids(self, form):
        """
        Retrieves ids of EmailAttachment ids that should be sent along with the email.

        Args:
            form (instance): ComposeEmailForm instance.

        Returns:
            A set containing EmailAttachment ids.
        """
        attachment_ids = set()
        for attachment_form in form.cleaned_data.get('attachments'):
            if attachment_form.cleaned_data and not attachment_form.cleaned_data['DELETE']:
                form_attachment = attachment_form.cleaned_data
                if form_attachment['id']:
                    # Only store attachment id for now
                    attachment_ids.add('%s' % form_attachment['id'].id)
        return attachment_ids

    def get_context_data(self, **kwargs):
        """
        Get context data that is used for the rendering of the template.

        Returns:
            A dict containing the context data.
        """
        context = super(EmailMessageComposeView, self).get_context_data(**kwargs)

        # Find email templates and add to context in json
        templates = EmailTemplate.objects.all()
        template_list = {}
        for template in templates:
            template_list.update({
                template.pk: {
                    'subject': template.subject,
                    'html_part': template.body_html,
                }
            })

        # Only add template_list to context if there are any templates.
        if template_list:
            context.update({
                'template_list': anyjson.serialize(template_list),
            })

        email_address = self.kwargs.get('email_address', None)
        recipient = None

        if email_address:
            recipient = Contact.objects.filter(
                email_addresses__email_address=email_address
            ).order_by('created').first()

            if not recipient:
                recipient = Account.objects.filter(
                    email_addresses__email_address=email_address
                ).order_by('created').first()

        if recipient:
            context.update({
                'recipient': recipient,
                'email_address': email_address
            })

        return context

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = 'new'

        email_address = self.kwargs.get('email_address', None)
        template = self.kwargs.get('template', None)

        if template:
            try:
                EmailTemplate.objects.get(pk=template)
            except EmailTemplate.DoesNotExist:
                try:
                    DefaultEmailTemplate.objects.get(user=get_current_user())
                except DefaultEmailTemplate.DoesNotExist:
                    message = _('Sorry, I couldn\'t load the given template. Please try a different one.')
                else:
                    message = _('Sorry, I couldn\'t load the given template. '
                                'I\'ll load your default email template instead.')

                messages.warning(self.request, message)
                template = None

        kwargs.update({
            'initial': {
                'send_to_normal': email_address,
                'template': template,
            },
        })

        return kwargs

    def get_success_url(self):
        success_url = self.request.POST.get('success_url', None)
        # Success url can be empty on send, so double check.
        if success_url:
            self.success_url = success_url

        return '/' + self.success_url

    def get_email_headers(self):
        """
        This function is not implemented. For custom headers overwrite this function.
        """
        return {}

    def send_message(self, email_outbox_message):
        """
        Creates a task for async sending an EmailOutboxMessage and sets messages for feedback.

        Args:
            email_outbox_message (instance): EmailOutboxMessage instance

        Returns:
            Task instance
        """
        send_logger = logging.getLogger('email_errors_temp_logger')

        send_logger.info('Begin creating task for email_outbox_message %d to %s' % (
            email_outbox_message.id, email_outbox_message.to
        ))

        task = send_message.apply_async(
            args=(email_outbox_message.id,),
            max_retries=1,
            default_retry_delay=100,
        )

        send_logger.info('Task (%s) status %s for email_outbox_message %d' % (
            task.id, task.status, email_outbox_message.id
        ))

        if task.status is not FAILURE:
            messages.info(
                self.request,
                _('Gonna deliver your email as fast as I can.')
            )
            self.request.session['tasks'].update({'send_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t send your email.')
            )
            send_logger.error(_('Failed to create send_message task (%s) outbox message id was %d. TRACE: %s') % (
                task.id, email_outbox_message.id, task.traceback
            ))

        # Remove the old draft when sending an email message.
        if self.object and self.remove_old_message:
            self.remove_draft()

        return task

    def remove_draft(self):
        """
        Removes the current draft.
        """
        task = trash_email_message.apply_async(args=(self.object.id,))

        try:
            email = EmailMessage.objects.get(pk=self.object.id)
            email._is_trashed = True  # Make sure the draft isn't shown immediately anymore.
            reindex_email_message(email)
        except EmailMessage.DoesNotExist:
            pass

        if not task:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t remove your email draft.')
            )
            logging.error(_('Failed to create remove_draft task for email account %d. Draft message id was %d.') % (
                self.object.send_from, self.object.id
            ))

        return task


class EmailMessageSendOrArchiveView(EmailMessageComposeView):

    def form_valid(self, form):
        email_outbox_message = super(EmailMessageSendOrArchiveView, self).form_valid(form)

        task = self.send_message(email_outbox_message)

        return email_outbox_message, task


class EmailMessageSendView(EmailMessageComposeView):

    def form_valid(self, form):
        email_outbox_message = super(EmailMessageSendView, self).form_valid(form)

        task = self.send_message(email_outbox_message)

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(self.get_success_url())


class EmailMessageDraftView(EmailMessageComposeView):

    def form_valid(self, form):
        email_message = super(EmailMessageDraftView, self).form_valid(form)

        if form.data.get('send_draft', False) == 'true':
            task = self.send_message(email_message)
        else:
            task = self.draft_message(email_message)

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(self.get_success_url())

    def draft_message(self, email_outbox_message):
        """
        Creates a task for async creating a draft and sets messages for feedback.

        Args:
            email_outbox_message (instance): EmailOutboxMessage instance

        Returns:
            Task instance
        """
        current_draft_pk = self.kwargs.get('pk', None)

        if current_draft_pk:
            try:
                email = EmailMessage.objects.get(pk=current_draft_pk)
                email._is_trashed = True  # Make sure the old draft isn't shown immediately anymore.
                reindex_email_message(email)
            except EmailMessage.DoesNotExist:
                pass

            task = update_draft_email_message.apply_async(
                args=(email_outbox_message.id, current_draft_pk,),
                max_retries=1,
                default_retry_delay=100,
            )
        else:
            task = create_draft_email_message.apply_async(
                args=(email_outbox_message.id,),
                max_retries=1,
                default_retry_delay=100,
            )

        if task:
            messages.info(
                self.request,
                _('Creating a draft as fast as I can.')
            )
            self.request.session['tasks'].update({'create_draft_email_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t save you email as a draft.')
            )
            logging.error(
                _('Failed to create create_draft_email_message task for email account %d. '
                  'Outbox message id was %d.') % (
                      email_outbox_message.send_from, email_outbox_message.id
                )
            )

        return task

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = 'draft'

        # Provide initial data if we're editing a draft.
        if self.object is not None:
            kwargs.update({
                'initial': {
                    'draft_pk': self.object.pk,
                    'send_from': self.object.account.id,
                    'subject': self.object.subject,
                    'send_to_normal': create_recipients(self.object.received_by.all()),
                    'send_to_cc': create_recipients(self.object.received_by_cc.all()),
                    'body_html': self.object.body_html,
                },
            })
        return kwargs


class EmailMessageReplyOrForwardView(EmailMessageComposeView):
    remove_old_message = False
    action = None

    def get_form_kwargs(self):
        kwargs = super(EmailMessageReplyOrForwardView, self).get_form_kwargs()
        kwargs['message_type'] = self.action
        return kwargs

    def get_subject(self, prefix='Re: '):
        subject = self.object.subject
        while True:
            if subject.lower().startswith('re:') or subject.lower().startswith('fw:'):
                subject = subject[3:].lstrip()
            elif subject.lower().startswith('fwd:'):
                subject = subject[4:].lstrip()
            else:
                break
        return u'%s%s' % (prefix, subject)

    def form_valid(self, form):
        email_outbox_message = super(EmailMessageReplyOrForwardView, self).form_valid(form)

        task = self.send_message(email_outbox_message)

        success_url = self.get_success_url()

        # Send and archive was pressed.
        if task and form.data.get('archive', False) == 'true':
            # An email message is archived by removing the inbox label and the provided label of the current inbox.
            current_inbox = form.data.get('current_inbox', '')

            # Filter out labels an user should not manipulate.
            remove_labels = []
            if current_inbox and current_inbox not in settings.GMAIL_LABELS_DONT_MANIPULATE:
                remove_labels.append(current_inbox)

            # Archiving email should always remove the inbox label.
            if settings.GMAIL_LABEL_INBOX not in remove_labels:
                remove_labels.append(settings.GMAIL_LABEL_INBOX)

            email_message = EmailMessage.objects.get(pk=self.object.id)
            email_message._is_archived = True
            labels_to_remove = EmailLabel.objects.filter(label_id__in=remove_labels,
                                                         account=self.object.account)
            email_message.labels.remove(*labels_to_remove)
            reindex_email_message(email_message)
            add_and_remove_labels_for_message.delay(self.object.id, remove_labels=remove_labels)

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(success_url)

    def send_message(self, email_outbox_message):
        """
        Creates a task to asynchronously send out a reply or forward an email message.

        Args:
            email_outbox_message (instance): EmailOutboxMessage instance

        Returns:
            Task instance
        """
        send_logger = logging.getLogger('email_errors_temp_logger')

        send_logger.info('Begin creating reply/forward task for email_outbox_message %d to %s' % (
            email_outbox_message.id, email_outbox_message.to
        ))

        task = send_message.apply_async(
            args=(email_outbox_message.id, self.object.id),
            max_retries=1,
            default_retry_delay=100,
        )

        send_logger.info('Reply/forward Task (%s) status %s for email_outbox_message %d' % (
            task.id, task.status, email_outbox_message.id
        ))

        if task:
            messages.info(
                self.request,
                _('Sending email as fast as I can.')
            )
            self.request.session['tasks'].update({'send_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t send your email.')
            )
            logging.error(_('Failed to create %s task for email account %d. Outbox message id was %d.') % (
                self.action,
                email_outbox_message.send_from,
                email_outbox_message.id,
            ))

        return task

    def get_email_headers(self):
        headers = super(EmailMessageReplyOrForwardView, self).get_email_headers()
        message_id = self.object.get_message_id()
        headers.update({
            'References': message_id,
        })

        return headers

    def get_success_url(self):
        """
        Return to previous email box after send, send & archive or forward.
        """
        return '/#/email'


class EmailMessageReplyView(EmailMessageReplyOrForwardView):
    action = 'reply'

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = self.action

        # Provide initial data.
        kwargs.update({
            'initial': {
                'subject': self.get_subject(prefix='Re: '),
                'send_to_normal': self.object.reply_to,
                'body_html': create_reply_body_header(self.object) + mark_safe(self.object.reply_body),
            },
        })

        return kwargs

    def get_email_headers(self):
        headers = super(EmailMessageReplyView, self).get_email_headers()
        message_id = self.object.get_message_id()
        headers.update({
            'In-Reply-To': message_id,
        })

        return headers


class EmailMessageReplyAllView(EmailMessageReplyView):
    action = 'reply_all'

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = self.action

        # Combine all the receivers into a single array
        # TODO: Once the sync is correct we might need to split this up
        # This means that send_to_normal will get all standard receivers
        # and send_to_cc will get all CC receivers
        receivers = list(chain(self.object.received_by.all(), self.object.received_by_cc.all()))
        filter_emails = [self.object.sender.email_address, self.object.account.email_address]

        recipients = create_recipients(receivers, filter_emails)

        # Provide initial data.
        kwargs.update({
            'initial': {
                'subject': self.get_subject(prefix='Re: '),
                'send_to_normal': self.object.reply_to,
                'send_to_cc': recipients,
                'body_html': create_reply_body_header(self.object) + mark_safe(self.object.reply_body),
            },
        })

        return kwargs


class EmailMessageForwardView(EmailMessageReplyOrForwardView):
    action = 'forward'

    def post(self, request, *args, **kwargs):
        """
        TODO: temporary override for logging purposes.
        """
        self.get_object(request, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(EmailMessageForwardView, self).get_form_kwargs()
        kwargs['message_type'] = self.action

        forward_header_to = []

        for recipient in self.object.received_by.all():
            if recipient.name:
                forward_header_to.append(recipient.name + ' &lt;' + recipient.email_address + '&gt;')
            else:
                forward_header_to.append(recipient.email_address)

        forward_header = (
            '<br /><br />'
            '<hr />'
            '---------- Forwarded message ---------- <br />'
            'From: ' + self.object.sender.email_address + '<br/>'
            'Date: ' + self.object.sent_date.ctime() + '<br/>'
            'Subject: ' + self.get_subject('') + '<br/>'
            'To: ' + ', '.join(forward_header_to) + '<br />'
        )

        # Provide initial data.
        kwargs.update({
            'initial': {
                'draft_pk': self.object.pk,
                'subject': self.get_subject(prefix='Fwd: '),
                'body_html': forward_header + mark_safe(self.object.reply_body),
            },
        })

        return kwargs

    def get_original_attachment_ids(self, form):
        """
        Add the original EmailAttachments from original message.

        Args:
            form (instance): ComposeEmailForm instance.

        Returns:
            A set containing EmailAttachment ids.
        """
        attachment_ids = super(EmailMessageReplyOrForwardView, self).get_original_attachment_ids(form)

        for id in form.cleaned_data.get('existing_attachments', []):
            attachment_ids.add(id)

        return attachment_ids


#
# EmailTemplate Views.
#
class EmailTemplateListView(LoginRequiredMixin, ListView):
    template_name = 'email/emailtemplate_list.html'
    model = EmailTemplate


class CreateUpdateEmailTemplateMixin(LoginRequiredMixin):
    form_class = CreateUpdateEmailTemplateForm
    model = EmailTemplate

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateEmailTemplateMixin, self).get_context_data(**kwargs)
        kwargs.update({
            'parameter_choices': anyjson.serialize(get_email_parameter_choices()),
            'back_url': self.get_success_url(),
        })
        return kwargs

    def get_success_url(self):
        """
        Return to email template list after creating or updating an email template.
        """
        return '/#/preferences/emailtemplates'


class CreateEmailTemplateView(CreateUpdateEmailTemplateMixin, CreateView):
    def form_valid(self, form):
        # Saves instance
        response = super(CreateEmailTemplateView, self).form_valid(form)

        # Show save messages
        message = _('%s has been created.') % self.object.name
        messages.success(self.request, message)

        post_intercom_event(event_name='email-template-created', user_id=self.request.user.id)

        return response


class UpdateEmailTemplateView(CreateUpdateEmailTemplateMixin, UpdateView):
    def form_valid(self, form):
        # Saves instance
        response = super(UpdateEmailTemplateView, self).form_valid(form)

        # Show save messages
        message = _('%s has been updated.') % self.object.name
        messages.success(self.request, message)

        return response


class EmailTemplateDeleteView(LoginRequiredMixin, FormActionMixin, StaticContextMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = EmailTemplate
    static_context = {'form_object_name': _('email template')}

    def delete(self, request, *args, **kwargs):
        response = super(EmailTemplateDeleteView, self).delete(request, *args, **kwargs)
        messages.success(self.request, _('%s (Email template) has been deleted.' % self.object.name))
        if is_ajax(self.request):
            return HttpResponse(anyjson.serialize({
                'error': False,
                'redirect_url': self.get_success_url()
            }), content_type='application/json')
        return response

    def get_success_url(self):
        return reverse('messaging_email_account_list')


class ParseEmailTemplateView(LoginRequiredMixin, FormView):
    """
    Parse an uploaded template for variables. This view is only used in AJAX calls.
    """
    form_class = EmailTemplateFileForm

    def form_valid(self, form):
        return HttpResponse(anyjson.serialize({
            'error': False,
            'form': form.cleaned_data
        }), content_type='application/json')

    def form_invalid(self, form):
        # Every form error will show up as a notification later
        for field, error in form.errors.items():  # pylint: disable=W0612
            messages.warning(self.request, error)

        return HttpResponse(anyjson.serialize({
            'error': True
        }), content_type='application/json')


class EmailTemplateGetDefaultView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        account_id = kwargs.pop('account_id')

        try:
            default_email_template_id = DefaultEmailTemplate.objects.get(
                user=request.user.pk,
                account_id=account_id
            ).template_id
        except DefaultEmailTemplate.DoesNotExist:
            default_email_template_id = None

        return HttpResponse(anyjson.serialize({
            'template_id': default_email_template_id,
        }), content_type='application/json')


class DetailEmailTemplateView(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        template = EmailTemplate.objects.get(pk=kwargs.get('template_id'))
        lookup = {'user': self.request.user}
        errors = {}

        if 'account_id' in self.request.GET:
            try:
                account = Account.objects.get(pk=self.request.GET.get('account_id'))
            except Account.DoesNotExist:
                pass
            else:
                lookup.update({'account': account})

        if 'contact_id' in self.request.GET:
            try:
                contact = Contact.objects.get(pk=self.request.GET.get('contact_id'))
            except Contact.DoesNotExist:
                pass
            else:
                lookup.update({'contact': contact})
                functions = contact.functions.all()
                if len(functions) == 1:
                    try:
                        account = Account.objects.get(pk=functions[0].account_id)
                    except Account.DoesNotExist:
                        pass
                    else:
                        lookup.update({'account': account})

        if 'document_id' in self.request.GET:
            credentials = get_credentials('pandadoc')

            if credentials:
                error_message = None
                document_id = self.request.GET.get('document_id')
                recipient = self.request.GET.get('recipient_email')

                details_url = 'https://api.pandadoc.com/public/v1/documents/%s/details' % document_id

                response = send_get_request(details_url, credentials)

                if response.status_code == 200:
                    # Only documents with the 'draft' status can be set to sent.
                    if response.json().get('status') == 'document.draft':
                        # Set the status of the document to 'sent' so we can create a view session.
                        send_url = 'https://api.pandadoc.com/public/v1/documents/%s/send' % document_id
                        send_params = {'silent': True}
                        response = send_post_request(send_url, credentials, send_params)

                        if response.status_code != 200:
                            error_message = 'Something went wrong while setting up the PandaDoc sign URL.'

                    metadata = response.json().get('metadata')

                    if metadata and metadata.get('account'):
                        account_id = metadata.get('account')

                        try:
                            account = Account.objects.get(pk=account_id)
                        except Account.DoesNotExist:
                            pass
                        else:
                            lookup.update({'account': account})

                    # Document has been 'sent' so create the session.
                    session_url = 'https://api.pandadoc.com/public/v1/documents/%s/session' % document_id
                    year = 60 * 60 * 24 * 365
                    session_params = {'recipient': recipient, 'lifetime': year}

                    response = send_post_request(session_url, credentials, session_params)

                    if response.status_code == 201:
                        sign_url = 'https://app.pandadoc.com/s/%s' % response.json().get('id')
                        lookup.update({'document': {'sign_url': sign_url}})
                    else:
                        error_message = ('The PandaDoc sign URL could not be created \
                                          because the recipient isn\'t correct')
                else:
                    error_message = 'The document doesn\'t seem to be valid.'

                if error_message:
                    errors.update({
                        'document': error_message
                    })

        if 'emailaccount_id' in self.request.GET:
            try:
                emailaccount = EmailAccount.objects.get(pk=self.request.GET.get('emailaccount_id'))
            except EmailAccount.DoesNotExist:
                pass
            else:
                lookup.get('user').current_email_address = emailaccount.email_address

        # Setup regex to find custom variables
        search_regex = '\[\[ custom\.(.*?) \]\]'
        # Find all occurrences.
        search_result = re.findall(search_regex, template.body_html)

        if search_result:
            for custom_variable in search_result:
                public = None

                try:
                    # Try to split to see if it's a public variable
                    variable, public = custom_variable.split('.')
                except ValueError:
                    # Not a public variable, so .split raises an error
                    variable = custom_variable

                if public:
                    template_variable = TemplateVariable.objects.filter(
                        name__iexact=variable,
                        is_public=True
                    )
                else:
                    template_variable = TemplateVariable.objects.filter(
                        name__iexact=variable,
                        owner=get_current_user()
                    )

                if template_variable:
                    # find = '\[\[ custom.' + custom_variable + '(\s)?\]\]'
                    find = re.compile('\[\[ custom\.' + custom_variable + ' \]\]')
                    replace = template_variable.first().text

                    template.body_html = re.sub(find, replace, template.body_html, 1)

        # Ugly hack to make parsing of new template brackets style work
        parsed_template = Template(template.body_html.replace('[[', '{{').replace(']]', '}}')).render(Context(lookup))
        parsed_subject = Template(template.subject.replace('[[', '{{').replace(']]', '}}')).render(Context(lookup))

        # Make sure HTML entities are displayed correctly
        html_parser = HTMLParser.HTMLParser()
        parsed_subject = html_parser.unescape(parsed_subject)

        attachments = []

        for attachment in template.attachments.all():
            # Get attachment name
            name = get_attachment_filename_from_url(attachment.attachment.name)

            attachments.append({
                'id': attachment.id,
                'name': name,
            })

        return HttpResponse(anyjson.serialize({
            'template': parsed_template,
            'template_subject': parsed_subject,
            'attachments': attachments,
            'errors': errors,
        }), content_type='application/json')


class CreateUpdateTemplateVariableMixin(LoginRequiredMixin):
    form_class = CreateUpdateTemplateVariableForm
    model = TemplateVariable

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateTemplateVariableMixin, self).get_context_data(**kwargs)
        kwargs.update({
            'parameter_choices': anyjson.serialize(get_email_parameter_choices()),
            'back_url': self.get_success_url(),
        })
        return kwargs

    def get_success_url(self):
        """
        Return to template variable list after creating or updating a template variable.
        """
        return '/#/preferences/templatevariables'


class CreateTemplateVariableView(CreateUpdateTemplateVariableMixin, CreateView):
    def form_valid(self, form):
        # Saves instance
        response = super(CreateTemplateVariableView, self).form_valid(form)

        # Show save messages
        message = _('%s has been created.') % self.object.name
        messages.success(self.request, message)

        post_intercom_event(event_name='email-variable-created', user_id=self.request.user.id)

        return response


class UpdateTemplateVariableView(CreateUpdateTemplateVariableMixin, UpdateView):
    def get_object(self, queryset=None):
        template_variable = super(UpdateTemplateVariableView, self).get_object(queryset=queryset)

        return template_variable

    def form_valid(self, form):
        # Saves instance
        response = super(UpdateTemplateVariableView, self).form_valid(form)

        # Show save messages
        message = _('%s has been updated.') % self.object.name
        messages.success(self.request, message)

        return response

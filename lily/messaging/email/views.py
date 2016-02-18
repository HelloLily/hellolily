from itertools import chain
import anyjson
import HTMLParser
import logging
import mimetypes
import re

from braces.views import StaticContextMixin
from bs4 import BeautifulSoup
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
from newrelic.agent import function_trace
from oauth2client.client import OAuth2WebServerFlow

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.google.token_generator import generate_token, validate_token
from lily.tenant.middleware import get_current_user
from lily.utils.functions import is_ajax
from lily.utils.views.mixins import LoginRequiredMixin, FormActionMixin, AjaxFormMixin

from .forms import (ComposeEmailForm, CreateUpdateEmailTemplateForm, CreateUpdateTemplateVariableForm,
                    EmailAccountCreateUpdateForm, EmailTemplateFileForm, EmailTemplateSetDefaultForm)
from .models.models import (EmailMessage, EmailAttachment, EmailAccount, EmailTemplate, DefaultEmailTemplate,
                            EmailOutboxMessage, EmailOutboxAttachment, TemplateVariable)
from .utils import (create_account, get_attachment_filename_from_url, get_email_parameter_choices,
                    create_recipients, render_email_body, replace_cid_in_html, create_reply_body_header)
from .tasks import (send_message, create_draft_email_message, delete_email_message, archive_email_message,
                    update_draft_email_message)


logger = logging.getLogger(__name__)


FLOW = OAuth2WebServerFlow(
    client_id=settings.GA_CLIENT_ID,
    client_secret=settings.GA_CLIENT_SECRET,
    redirect_uri=settings.GMAIL_CALLBACK_URL,
    scope='https://mail.google.com/',
    approval_prompt='force',
)


class SetupEmailAuth(LoginRequiredMixin, View):
    def get(self, request):
        FLOW.params['state'] = generate_token(settings.SECRET_KEY, request.user.pk)
        authorize_url = FLOW.step1_get_authorize_url()

        return HttpResponseRedirect(authorize_url)


class OAuth2Callback(LoginRequiredMixin, View):
    def get(self, request):
        if not validate_token(settings.SECRET_KEY, str(request.GET.get('state')), request.user.pk):
            return HttpResponseBadRequest()
        credentials = FLOW.step2_exchange(code=request.GET.get('code'))

        account = create_account(credentials, request.user)

        return HttpResponseRedirect('/#/preferences/emailaccounts/edit/%s' % account.pk)


class EmailAccountUpdateView(LoginRequiredMixin, AjaxFormMixin, SuccessMessageMixin, FormActionMixin,
                             StaticContextMixin, UpdateView):
    template_name = 'ajax_form.html'
    model = EmailAccount
    form_class = EmailAccountCreateUpdateForm
    success_message = _('%(label)s has been updated.')
    static_context = {'form_prevent_autofill': True}

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(EmailAccountUpdateView, self).get_context_data(**kwargs)
        if not is_ajax(self.request):
            kwargs.update({
                'back_url': self.get_success_url(),
            })

        return kwargs

    def get(self, request, *args, **kwargs):
        if not is_ajax(request):
            self.template_name = 'form.html'

        return super(EmailAccountUpdateView, self).get(request, *args, **kwargs)

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
# EmailMessage compose views (create/edit draft, reply, forward) incl. preview
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

                self.object.body_html = replace_cid_in_html(self.object.body_html, attachments, request)
            except EmailMessage.DoesNotExist:
                pass

    def form_valid(self, form):
        """
        Process form to do either of these actions:
            - send an email message
        """
        email_draft = form.cleaned_data
        email_account = email_draft['send_from']
        soup = BeautifulSoup(email_draft['body_html'], 'lxml', from_encoding='utf-8')
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

        original_attachment_ids = set()
        for attachment_form in form.cleaned_data.get('attachments'):
            if attachment_form.cleaned_data and not attachment_form.cleaned_data['DELETE']:
                form_attachment = attachment_form.cleaned_data
                if form_attachment['id']:
                    # Only store attachment id for now
                    original_attachment_ids.add('%s' % form_attachment['id'].id)
                else:
                    # Uploaded file, add it to email_outbox_message
                    outbox_attachment = EmailOutboxAttachment()
                    outbox_attachment.attachment = form_attachment['attachment']
                    outbox_attachment.content_type = form_attachment['attachment'].content_type
                    outbox_attachment.email_outbox_message = email_outbox_message
                    outbox_attachment.size = form_attachment['attachment'].size
                    outbox_attachment.save()

        # Store the ids of the original message attachments
        email_outbox_message.original_attachment_ids = ','.join(original_attachment_ids)
        email_outbox_message.save()

        # Remove an old draft when sending an e-mail message or saving a new draft
        if self.object and self.remove_old_message:
            self.remove_draft()

        return email_outbox_message

    def get_context_data(self, **kwargs):
        """
        Get context data that is used for the rendering of the template.

        Returns:
            A dict containing the context data.
        """
        context = super(EmailMessageComposeView, self).get_context_data(**kwargs)

        # Find e-mail templates and add to context in json
        templates = EmailTemplate.objects.all()
        template_list = {}
        for template in templates:
            template_list.update({
                template.pk: {
                    'subject': template.subject,
                    'html_part': template.body_html,
                }
            })

        # Only add template_list to context if there are any templates
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
                    message = _('Sorry, I couldn\'t load the given template. Please try a different one')
                else:
                    message = _('Sorry, I couldn\'t load the given template. '
                                'I\'ll load your default email template instead')

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
        # Success url can be empty on send, so double check
        if success_url:
            self.success_url = success_url

        return '/' + self.success_url

    def get_email_headers(self):
        """
        This function is not implemented. For custom headers overwrite this function.
        """
        return {}

    def remove_draft(self):
        """
        This function is not implemented jet.

        Removes the current draft.
        """
        task = delete_email_message.apply_async(args=(self.object.id,))

        if not task:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t remove your e-mail draft')
            )
            logging.error(_('Failed to create remove_draft task for email account %d. Draft message id was %d.') % (
                self.object.send_from, self.object.id
            ))

        return task


class EmailMessageSendOrArchiveView(EmailMessageComposeView):

    def send_message(self, email_outbox_message):
        """
        Creates and task for async sending an EmailOutboxMessage and sets messages for feedback.

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
                _('Gonna deliver your email as fast as I can')
            )
            self.request.session['tasks'].update({'send_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t deliver your e-mail, but I did save it as a draft so you can try again later')
            )
            send_logger.error(_('Failed to create send_message task (%s) outbox message id was %d. TRACE: %s') % (
                task.id, email_outbox_message.id, task.traceback
            ))

        return task

    def form_valid(self, form):
        email_outbox_message = super(EmailMessageSendOrArchiveView, self).form_valid(form)

        task = self.send_message(email_outbox_message)

        return email_outbox_message, task


class EmailMessageSendView(EmailMessageSendOrArchiveView):

    def form_valid(self, form):
        email_outbox_message, task = super(EmailMessageSendView, self).form_valid(form)

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(self.get_success_url())


class EmailMessageDraftView(EmailMessageComposeView):

    def form_valid(self, form):
        email_message = super(EmailMessageDraftView, self).form_valid(form)

        task = self.draft_message(email_message)

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(self.get_success_url())

    def draft_message(self, email_outbox_message):
        """
        Creates and task for async sending an EmailOutboxMessage and sets messages for feedback.

        Args:
            email_outbox_message (instance): EmailOutboxMessage instance

        Returns:
            Task instance
        """
        current_draft_pk = self.kwargs.get('pk', None)

        if current_draft_pk:
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
                _('Creating a draft as fast as I can')
            )
            self.request.session['tasks'].update({'create_draft_email_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t save you e-mail as a draft')
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

        # Provide initial data if we're editing a draft
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
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
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

        # Send and archive was pressed, so start an archive task
        if task and form.data.get('archive', False) == 'true':
            success_url = '/#/email'  # Exception for archiving, go to inbox
            archive_email_message.apply_async(args=(self.object.id,))

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(success_url)

    def send_message(self, email_outbox_message):
        """
        Creates a task to asynchronously reply on an email message.

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
                _('Sending email as fast as I can')
            )
            self.request.session['tasks'].update({'send_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t send your e-mail')
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


class EmailMessageReplyView(EmailMessageReplyOrForwardView):
    action = 'reply'

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = self.action

        # Provide initial data
        kwargs.update({
            'initial': {
                'subject': self.get_subject(prefix='Re: '),
                'send_to_normal': self.object.sender.email_address,
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

        # Provide initial data
        kwargs.update({
            'initial': {
                'subject': self.get_subject(prefix='Re: '),
                'send_to_normal': self.object.sender.email_address,
                'send_to_cc': recipients,
                'body_html': create_reply_body_header(self.object) + mark_safe(self.object.reply_body),
            },
        })

        return kwargs


class EmailMessageForwardView(EmailMessageReplyOrForwardView):
    action = 'forward'

    @function_trace()
    def post(self, request, *args, **kwargs):
        return super(EmailMessageForwardView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
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

        # Provide initial data
        kwargs.update({
            'initial': {
                'draft_pk': self.object.pk,
                'subject': self.get_subject(prefix='Fwd: '),
                'body_html': forward_header + mark_safe(self.object.reply_body),
            },
        })

        return kwargs


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
        message = _('%s has been created') % self.object.name
        messages.success(self.request, message)

        return response


class UpdateEmailTemplateView(CreateUpdateEmailTemplateMixin, UpdateView):
    def form_valid(self, form):
        # Saves instance
        response = super(UpdateEmailTemplateView, self).form_valid(form)

        # Show save messages
        message = _('%s has been updated') % self.object.name
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


class EmailTemplateSetDefaultView(LoginRequiredMixin, FormActionMixin, SuccessMessageMixin, AjaxFormMixin, UpdateView):
    template_name = 'form.html'
    model = EmailTemplate
    form_class = EmailTemplateSetDefaultForm

    def get_success_message(self, cleaned_data):
        default_for = self.object.default_for.all()
        default_for_length = len(default_for)
        if default_for_length == 0:
            message = _('%s is no longer a default template' % self.object)
        elif default_for_length == 1:
            message = _('%s has been set as default for: %s' % (self.object, default_for[0]))
        else:
            message = _('%s has been set as default for: %s and %s others' % (
                self.object, default_for[0], default_for_length - 1
            ))
        return message

    def get_success_url(self):
        return '/#/preferences/emailtemplates'


class EmailTemplateGetDefaultView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        account_id = kwargs.pop('account_id')

        try:
            email_account = EmailAccount.objects.get(pk=account_id)
        except EmailAccount.DoesNotExist:
            raise Http404()
        else:
            default_email_template_id = None

            try:
                current_user = get_current_user()
                default_email_template = email_account.default_templates.get(user_id=current_user.id)
                default_email_template_id = default_email_template.template.id
            except DefaultEmailTemplate.DoesNotExist:
                pass

            return HttpResponse(anyjson.serialize({
                'template_id': default_email_template_id,
            }), content_type='application/json')


class DetailEmailTemplateView(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        template = EmailTemplate.objects.get(pk=kwargs.get('template_id'))
        lookup = {'user': self.request.user}

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

        if 'emailaccount_id' in self.request.GET:
            try:
                emailaccount = EmailAccount.objects.get(pk=self.request.GET.get('emailaccount_id'))
            except EmailAccount.DoesNotExist:
                pass
            else:
                lookup.get('user').current_email_address = emailaccount.email_address

        # Setup regex to find custom variables
        search_regex = '\[\[ custom\.(.*?) \]\]'
        # Find all occurences
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
        message = _('%s has been created') % self.object.name
        messages.success(self.request, message)

        return response


class UpdateTemplateVariableView(CreateUpdateTemplateVariableMixin, UpdateView):
    def get_object(self, queryset=None):
        """
        A user is only able to edit accounts he owns.
        """
        template_variable = super(UpdateTemplateVariableView, self).get_object(queryset=queryset)
        if not template_variable.owner == self.request.user and not template_variable.is_public:
            raise Http404()

        return template_variable

    def form_valid(self, form):
        # Saves instance
        response = super(UpdateTemplateVariableView, self).form_valid(form)

        # Show save messages
        message = _('%s has been updated') % self.object.name
        messages.success(self.request, message)

        return response

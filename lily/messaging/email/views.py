import anyjson
import logging
import mimetypes

from braces.views import StaticContextMixin
from bs4 import BeautifulSoup
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
from python_imap.utils import extract_tags_from_soup
from oauth2client.client import OAuth2WebServerFlow

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.google.token_generator import generate_token, validate_token
from lily.tenant.middleware import get_current_user
from lily.utils.functions import is_ajax
from lily.utils.views import AngularView
from lily.utils.views.mixins import LoginRequiredMixin, FormActionMixin, AjaxFormMixin

from .forms import (EmailAccountShareForm, EmailAccountCreateUpdateForm, CreateUpdateEmailTemplateForm,
                    EmailTemplateFileForm, EmailTemplateSetDefaultForm, ComposeEmailForm)
from .models.models import (EmailMessage, EmailAttachment, EmailAccount, EmailTemplate, DefaultEmailTemplate,
                            EmailOutboxMessage, EmailTemplateAttachment, EmailOutboxAttachment)
from .utils import create_account, get_attachment_filename_from_url, get_email_parameter_choices, create_task_status
from .tasks import send_message, archive_email_message, create_draft_email_message, delete_email_message


logger = logging.getLogger(__name__)


class EmailBaseView(LoginRequiredMixin, AngularView):
    def get_template_names(self):
        return 'email/%s' % self.kwargs.get('template_file', 'email_base.html')


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
        if not validate_token(settings.SECRET_KEY, request.GET.get('state'), request.user.pk):
            return HttpResponseBadRequest()
        credentials = FLOW.step2_exchange(code=request.GET.get('code'))

        account = create_account(credentials, request.user)

        return HttpResponseRedirect(reverse('messaging_email_account_update', args=[account.pk]))


class EmailAccountListView(LoginRequiredMixin, DetailView):
    template_name = 'email/emailaccount_list.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(EmailAccountListView, self).get_context_data(**kwargs)

        context.update({
            'user_email_accounts': self.object.email_accounts_owned.filter(is_deleted=False).exclude(public=True),
            'shared_email_accounts': self.object.shared_email_accounts.filter(is_deleted=False),
            'company_email_accounts': EmailAccount.objects.filter(is_deleted=False, public=True)
        })

        return context


class EmailAccountShareView(LoginRequiredMixin, FormActionMixin, SuccessMessageMixin, AjaxFormMixin, UpdateView):
    template_name = 'ajax_form.html'
    model = EmailAccount
    form_class = EmailAccountShareForm

    def get_success_message(self, cleaned_data):
        return _('%(account)s has been updated' % {'account': self.object.label})

    def get_object(self, queryset=None):
        email_account = super(EmailAccountShareView, self).get_object(queryset)
        if not email_account.is_owned_by_user:
            raise Http404()

        return email_account

    def get_success_url(self):
        return reverse('messaging_email_account_list')


class EmailAccountUpdateView(LoginRequiredMixin, AjaxFormMixin, SuccessMessageMixin, FormActionMixin, StaticContextMixin, UpdateView):
    template_name = 'ajax_form.html'
    model = EmailAccount
    form_class = EmailAccountCreateUpdateForm
    success_message = _('%(label)s has been updated.')
    static_context = {'form_prevent_autofill': True}

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
        return reverse('messaging_email_account_list')


class EmailAccountDeleteView(LoginRequiredMixin, FormActionMixin, StaticContextMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = EmailAccount
    static_context = {'form_object_name': _('email account')}

    def get_object(self, queryset=None):
        email_account = super(EmailAccountDeleteView, self).get_object(queryset)
        if not email_account.is_owned_by_user and not email_account.is_public:
            raise Http404()

        return email_account

    def delete(self, request, *args, **kwargs):
        response = super(EmailAccountDeleteView, self).delete(request, *args, **kwargs)
        messages.success(self.request, _('%(label)s (%(email_address)s) has been deleted.' % {
            'label': self.object.label,
            'email_address': self.object.email_address,
        }))

        if is_ajax(self.request):
            return HttpResponse(anyjson.serialize({
                'error': False,
                'redirect_url': self.get_success_url()
            }), content_type='application/json')
        return response

    def get_success_url(self):
        return reverse('messaging_email_account_list')


class EmailMessageHTMLView(LoginRequiredMixin, DetailView):
    """
    Display an email body in an isolated html.
    """
    model = EmailMessage
    template_name = 'email/emailmessage_html.html'

    def get_queryset(self):
        queryset = super(EmailMessageHTMLView, self).get_queryset()

        return queryset.filter(account__tenant=self.request.user.tenant)


class EmailAttachmentProxy(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        try:
            attachment = EmailAttachment.objects.get(pk=pk, message__account__tenant_id=self.request.user.tenant.id)
        except:
            raise Http404()

        s3_file = default_storage._open(attachment.attachment.name)

        wrapper = FileWrapper(s3_file)
        if hasattr(s3_file, 'key'):
            content_type = s3_file.key.content_type
        else:
            content_type = mimetypes.guess_type(s3_file.file.name)[0]

        response = HttpResponse(wrapper, content_type=content_type)

        response['Content-Disposition'] = 'attachment; filename=%s' % get_attachment_filename_from_url(s3_file.name)
        response['Content-Length'] = attachment.size
        return response


#
# EmailMessage compose views (create/edit draft, reply, forward) incl. preview
#
class EmailMessageComposeView(FormView):
    template_name = 'email/emailmessage_compose.html'
    form_class = ComposeEmailForm
    object = None
    remove_old_message = True

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
            except EmailMessage.DoesNotExist:
                pass

    def form_valid(self, form):
        """
        Process form to do either of these actions:
            - send an email message
        """
        email_draft = form.cleaned_data

        email_account = email_draft['send_from']

        soup = BeautifulSoup(email_draft['body_html'], 'permissive')
        soup = extract_tags_from_soup(soup, settings.BLACKLISTED_EMAIL_TAGS)

        # Replace the src attribute of inline images with a Content-ID for each image
        inline_application_url = '/messaging/email/attachment/'
        inline_application_images = soup.findAll('img', {
            'src': lambda src: src and src.startswith(inline_application_url)
        })

        # Mapping {attachment.pk : image element}
        mapped_attachments = {}
        for image in inline_application_images:
            # Parse attachment pks from image paths
            pk_and_path = image.get('src')[len(inline_application_url):].rstrip('/')
            pk = int(pk_and_path.split('/')[0])
            mapped_attachments[pk] = image

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
            mapped_attachments=len(mapped_attachments.keys())
        )

        for attachment_form in form.cleaned_data.get('attachments'):
            if not attachment_form.cleaned_data['DELETE']:
                uploaded_attachment = attachment_form.cleaned_data['attachment']
                attachment = attachment_form.save(commit=False)
                attachment.content_type = uploaded_attachment.content_type
                attachment.size = uploaded_attachment.size
                attachment.email_outbox_message = email_outbox_message
                attachment.save()

        template_attachment_ids = self.request.POST.get('template_attachment_ids').split(',')
        for template_attachment_id in template_attachment_ids:
            # An empty string gives a ValueError, so check for an empty string
            if template_attachment_id:
                try:
                    template_attachment = EmailTemplateAttachment.objects.get(pk=template_attachment_id)
                except EmailTemplateAttachment.DoesNotExist:
                    pass
                else:
                    attachment = EmailOutboxAttachment()
                    attachment.content_type = template_attachment.content_type
                    attachment.size = template_attachment.size
                    attachment.email_outbox_message = email_outbox_message
                    attachment.attachment = template_attachment.attachment
                    attachment.save()

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

        # find e-mail templates and add to context in json
        templates = EmailTemplate.objects.all()
        template_list = {}
        for template in templates:
            template_list.update({
                template.pk: {
                    'subject': template.subject,
                    'html_part': template.body_html,
                }
            })

        # only add template_list to context if there are any templates
        if template_list:
            context.update({
                'template_list': anyjson.serialize(template_list),
            })

        return context

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = 'new'

        return kwargs

    def get_success_url(self):
        return reverse('messaging_email_inbox')

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
        status = create_task_status('send_message')

        task = send_message.apply_async(
            args=(email_outbox_message.id,),
            max_retries=1,
            default_retry_delay=100,
            kwargs={'status_id': status.pk},
        )

        status.task_id = task.id
        status.save()

        if task:
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
            logging.error(_('Failed to create send_message task for email account %d. Outbox message id was %d.') % (
                email_outbox_message.send_from, email_outbox_message.id
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


class EmailMessageSendAndArchiveView(EmailMessageSendOrArchiveView):
    def form_valid(self, form):
        email_outbox_message, task = super(EmailMessageSendAndArchiveView, self).form_valid(form)

        status = create_task_status('archive_message')

        task = archive_email_message.apply_async(
            args=(self.object.id,),
            max_retries=1,
            default_retry_delay=100,
            kwargs={'status_id': status.pk},
        )

        status.task_id = task.id
        status.save()

        if not task:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t archive your e-mail. You should try to archive it again later')
            )
            logging.error(_('Failed to create archive_message task for email account %d. Message id was %d') % (
                email_outbox_message.send_from.id,
                self.object.id
            ))

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
        status = create_task_status('create_draft_email_message')

        task = create_draft_email_message.apply_async(
            args=(email_outbox_message.id,),
            max_retries=1,
            default_retry_delay=100,
            kwargs={'status_id': status.pk},
        )

        status.task_id = task.id
        status.save()

        if task:
            messages.info(
                self.request,
                _('Saving email as fast as I can')
            )
            self.request.session['tasks'].update({'create_draft_email_message': task.id})
            self.request.session.modified = True
        else:
            messages.error(
                self.request,
                _('Sorry, I couldn\'t save your e-mail')
            )
            logging.error(_('Failed to create create_draft_email_message task for email account %d. Outbox message id was %d.') % (
                email_outbox_message.send_from, email_outbox_message.id
            ))

        return task

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = 'draft'

        # Provide initial data if we're editing a draft
        if self.object is not None:
            kwargs.update({
                'draft_id': self.object.pk,
                'initial': {
                    'send_from': self.object.sender,
                    'subject': self.object.subject,
                    'send_to_normal': ','.join(self.object.received_by.all().values_list('email_address', flat=True)),
                    'send_to_cc': ','.join(self.object.received_by_cc.all().values_list('email_address', flat=True)),
                    'body_html': self.object.body_html,
                },
            })
        return kwargs


class EmailMessageReplyView(EmailMessageComposeView):
    remove_old_message = False

    def get_form_kwargs(self):
        kwargs = super(EmailMessageComposeView, self).get_form_kwargs()
        kwargs['message_type'] = 'reply'

        # Provide initial data
        if self.object is not None:
            kwargs.update({
                'initial': {
                    'subject': self.get_subject(),
                    'send_to_normal': self.object.sender.email_address,
                    'body_html': mark_safe(self.object.reply_body),
                },
            })
        return kwargs

    def get_subject(self, prefix='Re: '):
        subject = self.object.subject
        while True:
            if subject.lower().startswith('re:') or subject.lower().startswith('fw:'):
                subject = subject[3:].lstrip()
            else:
                break
        return u'%s%s' % (prefix, subject)

    def form_valid(self, form):
        email_outbox_message = super(EmailMessageReplyView, self).form_valid(form)

        task = self.reply_message(email_outbox_message)

        if is_ajax(self.request):
            return HttpResponse(anyjson.dumps({'task_id': task.id}), content_type='application/json')
        else:
            return HttpResponseRedirect(self.get_success_url())

    def reply_message(self, email_outbox_message):
        """
        Creates a task for async replyen on a message with an EmailOutboxMessage and sets messages for feedback.

        Args:
            email_outbox_message (instance): EmailOutboxMessage instance

        Returns:
            Task instance
        """
        status = create_task_status('send_message')

        task = send_message.apply_async(
            args=(email_outbox_message.id, self.object.id),
            max_retries=1,
            default_retry_delay=100,
            kwargs={'status_id': status.pk},
        )

        status.task_id = task.id
        status.save()

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
            logging.error(_('Failed to create reply_on_email_message task for email account %d. Outbox message id was %d.') % (
                email_outbox_message.send_from, email_outbox_message.id
            ))

        return task

    def get_email_headers(self):
        headers = super(EmailMessageReplyView, self).get_email_headers()
        message_id = self.object.get_message_id()
        headers.update({
            'References': message_id,
            'In-Reply-To': message_id,
        })

        return headers


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
        return reverse('messaging_email_template_list')


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
    template_name = 'ajax_form.html'
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
            message = _('%s has been set as default for: %s and %s others' % (self.object, default_for[0], default_for_length - 1))
        return message

    def get_success_url(self):
        return reverse('messaging_email_account_list')


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

        parsed_template = Template(template.body_html).render(Context(lookup))

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
            'attachments': attachments,
        }), content_type='application/json')

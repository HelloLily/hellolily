import datetime
import email
import traceback
import urllib
import logging

from dateutil.tz import tzutc
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from lily.contacts.models import Contact
from lily.messaging.email.emailclient import LilyIMAP, DRAFTS, INBOX, SENT, TRASH, SPAM, ALLMAIL
from lily.messaging.email.forms import CreateUpdateEmailTemplateForm, \
    EmailTemplateFileForm, ComposeEmailForm, EmailConfigurationStep1Form, \
    EmailConfigurationStep2Form, EmailConfigurationStep3Form
from lily.messaging.email.models import EmailMessage, EmailAccount, EmailTemplate, EmailProvider
from lily.messaging.email.tasks import save_email_messages, mark_messages, synchronize_folder
from lily.messaging.email.utils import get_email_parameter_choices, flatten_html_to_text, TemplateParser
from lily.tenant.middleware import get_current_user
from lily.utils.functions import uniquify
from lily.utils.models import EmailAddress
from lily.utils.views import DeleteBackAddSaveFormViewMixin, FilteredListMixin, SortedListMixin


log = logging.getLogger('django.request')


class EditEmailAccountView(TemplateView):
    """
    Edit an existing e-mail account.
    """
    template_name = 'messaging/email/account_create.html'


class DetailEmailAccountView(TemplateView):
    """
    Show the details of an existing e-mail account.
    """
    template_name = 'messaging/email/account_create.html'


class ListEmailTemplateView(SortedListMixin, FilteredListMixin, ListView):
    template_name = 'messaging/email/email_template_list.html'
    model = EmailTemplate
    sortable = [1, 2]
    default_order_by = 2

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListEmailTemplateView, self).get_context_data(**kwargs)

        kwargs.update({
            'list_item_template': 'messaging/email/email_template_list_item.html',
        })

        return kwargs


class AddEmailTemplateView(DeleteBackAddSaveFormViewMixin, CreateView):
    """
    Create a new e-mail template that can be used for sending emails.
    """
    template_name = 'messaging/email/template_create_or_update.html'
    model = EmailTemplate
    form_class = CreateUpdateEmailTemplateForm

    def get_context_data(self, **kwargs):
        """

        :param kwargs: keyword arguments.
        :return: context data used to render the template.
        """
        context = super(AddEmailTemplateView, self).get_context_data(**kwargs)
        context.update({
            'parameter_choices': simplejson.dumps(get_email_parameter_choices()),
        })
        return context

    def get_success_url(self):
        """
        Redirect to the inbox view.
        """
        messages.success(self.request, _('Template saved successfully.'))

        return reverse('messaging_email_inbox')


class EditEmailTemplateView(DeleteBackAddSaveFormViewMixin, UpdateView):
    """
    Parse an uploaded template for variables and return a generated form/
    """
    template_name = 'messaging/email/template_create_or_update.html'
    model = EmailTemplate
    form_class = CreateUpdateEmailTemplateForm

    def get_context_data(self, **kwargs):
        context = super(EditEmailTemplateView, self).get_context_data(**kwargs)
        context.update({
            'parameter_choices': simplejson.dumps(get_email_parameter_choices()),
        })
        return context

    def get_success_url(self):
        """
        Redirect to the edit view, so the default values of parameters can be filled in.
        """
        messages.success(self.request, _('Template edited successfully.'))

        return reverse('messaging_email_inbox')

    def get_form_kwargs(self):
        """
        Get the keyword arguments that will be used to initiate the form.

        :return: An dict of keyword arguments.
        """
        kwargs = super(EditEmailTemplateView, self).get_form_kwargs()
        kwargs.update({
            'draft_id': self.object.pk,
            'message_type': 'template',
        })
        return kwargs


class ParseEmailTemplateView(FormView):
    """
    Parse an uploaded template for variables and return a generated form
    """
    template_name = 'messaging/email/template_create_or_update_base_form.html'
    form_class = EmailTemplateFileForm

    def form_valid(self, form):
        """
        Return parsed form with rendered parameter fields
        """
        # we return content of the file here because this easily enables us to do more sophisticated parsing in the future.
        form.cleaned_data.update({
            'valid': True,
        })

        return HttpResponse(simplejson.dumps(form.cleaned_data), mimetype="application/json")

    def form_invalid(self, form):
        return HttpResponse(simplejson.dumps({
            'valid': False,
            'errors': form.errors,
        }), mimetype="application/json")


class EmailFolderView(ListView):
    """
    Show a list of e-mail messages in a certain folder.
    """
    template_name = 'messaging/email/model_list.html'
    paginate_by = 10
    folder_name = None
    folder_identifier = None

    def get(self, request, *args, **kwargs):
        # Determine which accounts to show messages from
        if kwargs.get('account_id'):
            self.messages_accounts = request.user.messages_accounts.filter(pk__in=[kwargs.get('account_id')])
        else:
            ctype = ContentType.objects.get_for_model(EmailAccount)
            self.messages_accounts = request.user.messages_accounts.filter(polymorphic_ctype=ctype)

            # Uniquify accounts, doubles are possible via personal, group, shared access etc.
            self.messages_accounts = uniquify(self.messages_accounts.order_by('emailaccount__email__email_address'), filter=lambda x: x.emailaccount.email.email_address)

        # Deteremine which folder to show messages from
        if kwargs.get('folder') and not any([self.folder_name, self.folder_identifier]):
            self.folder_name = self.folder_identifier = urllib.unquote_plus(kwargs.get('folder'))

        return super(EmailFolderView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return empty queryset or return it filtered based on folder_name and/or folder_identifier.
        """
        qs = EmailMessage.objects.none()
        if self.folder_name is not None and self.folder_identifier is not None:
            qs = EmailMessage.objects.filter(Q(folder_identifier=self.folder_identifier.lstrip('\\')) | Q(folder_name=self.folder_name))
        elif self.folder_name is not None:
            qs = EmailMessage.objects.filter(folder_name=self.folder_name)
        elif self.folder_identifier is not None:
            qs = EmailMessage.objects.filter(folder_identifier=self.folder_identifier.lstrip('\\'))
        return qs.filter(account__in=self.messages_accounts).order_by('-sent_date')

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(EmailFolderView, self).get_context_data(**kwargs)
        kwargs.update({
            'list_item_template': 'messaging/email/model_list_item.html',
            'list_title': ', '.join([messaging_account.email.email_address for messaging_account in self.messages_accounts]),
        })

        # Also pass search parameters, if any
        kwargs.update({
            'selected_email_account_id': self.kwargs.get('account_id', ''),
            'selected_email_folder': urllib.quote_plus(self.kwargs.get('folder', self.folder_name or self.folder_identifier)),
            'email_search_key': self.kwargs.get('search_key', '')
        })

        return kwargs


class EmailInboxView(EmailFolderView):
    """
    Show INBOX folder for all accessible messages accounts.
    """
    folder_identifier = INBOX


class EmailDraftsView(EmailFolderView):
    """
    Show DRAFTS folder for all accessible messages accounts.
    """
    folder_identifier = DRAFTS


class EmailSentView(EmailFolderView):
    """
    Show SENT folder for all accessible messages accounts.
    """
    folder_identifier = SENT


class EmailTrashView(EmailFolderView):
    """
    Show TRASH folder for all accessible messages accounts.
    """
    folder_identifier = TRASH


class EmailSpamView(EmailFolderView):
    """
    Show SPAM folder for all accessible messages accounts.
    """
    folder_identifier = SPAM


class EmailMessageJSONView(View):
    """
    Show most attributes of an EmailMessage in JSON format.
    """
    http_method_names = ['get']
    template_name = 'messaging/email/email_heading.html'

    def get(self, request, *args, **kwargs):
        """
        Retrieve the email for the requested uid from the database or directly via IMAP.
        """
        # Convert date to epoch
        def unix_time(dt):
            epoch = datetime.datetime.fromtimestamp(0, tz=dt.tzinfo)
            delta = dt - epoch
            return delta.total_seconds()

        def unix_time_millis(dt):
            return unix_time(dt) * 1000.0

        # Find account
        ctype = ContentType.objects.get_for_model(EmailAccount)
        self.messages_accounts = request.user.messages_accounts.filter(polymorphic_ctype=ctype)
        server = None
        try:
            instance = EmailMessage.objects.get(id=kwargs.get('pk'))
            # See if the user has access to this message
            if instance.account not in self.messages_accounts:
                raise Http404()

            # if (instance.body_html is None or len(instance.body_html.strip()) == 0) and (instance.body_text is None or len(instance.body_text.strip()) == 0):
            if True:
                # Retrieve directly from IMAP (marks as read automatically)
                server = LilyIMAP(provider=instance.account.provider, account=instance.account)
                message = server.get_modifiers_for_uid(instance.uid, modifiers=['BODY[]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE'], folder=instance.folder_name)
                if len(message):
                    folder = server.get_folder(message.get('folder_name'))
                    save_email_messages({instance.uid: message}, instance.account, folder.get_server_name(), folder.identifier)

                instance = EmailMessage.objects.get(id=kwargs.get('pk'))
            else:
                # Mark as read manually
                mark_messages.delay(instance.id, read=True)
            instance.is_seen = True
            instance.save()

            message = {
                'id': instance.id,
                'sent_date': unix_time_millis(instance.sent_date),
                'flags': instance.flags,
                'uid': instance.uid,
                'flat_body': truncatechars(instance.body_text, 200),
                'subject': instance.subject.encode('utf-8'),
                'size': instance.size,
                'is_private': instance.is_private,
                'is_read': instance.is_seen,
                'is_plain': instance.is_plain,
                'folder_name': instance.folder_name,
            }

            # Replace body with a more richer version of an e-mail view
            message['body'] = render_to_string(self.template_name, {'object': instance})
            return HttpResponse(simplejson.dumps(message), mimetype='application/json; charset=utf-8')
        except EmailMessage.DoesNotExist:
            raise Http404()
        finally:
            if server:
                server.logout()


class EmailMessageHTMLView(View):
    """
    Return the HTML for single e-mail message.
    """
    http_method_names = ['get']
    template_name = 'messaging/email/email_body.html'

    def get(self, request, *args, **kwargs):
        try:
            instance = EmailMessage.objects.get(id=kwargs.get('pk'))
            if instance.body_html:
                body = render_to_string(self.template_name, {'is_plain': False, 'body': instance.body_html.encode('utf-8')})
            else:
                body = render_to_string(self.template_name, {'is_plain': True, 'body': instance.body_text.encode('utf-8')})

            return HttpResponse(body, mimetype='text/html; charset=utf-8')
        except EmailMessage.DoesNotExist:
            raise Http404()


class MessageUpdateView(View):
    """
    Handle various AJAX calls for n messages.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            message_ids = request.POST.getlist('ids[]')
            if not isinstance(message_ids, list):
                message_ids = [message_ids]
            if len(message_ids) > 0:
                self.handle_message_update(message_ids)
        except:
            raise Http404()

        # Return response
        return HttpResponse(simplejson.dumps({}), mimetype='application/json')

    def handle_message_update(self, message_ids):
        raise NotImplementedError("Implement by subclassing MessageUpdateView")


class MarkReadAjaxView(MessageUpdateView):
    """
    Mark messages as read.
    """
    def handle_message_update(self, message_ids):
        mark_messages.delay(message_ids, read=True)


class MarkUnreadAjaxView(MessageUpdateView):
    """
    Mark messages as unread.
    """
    def handle_message_update(self, message_ids):
        mark_messages.delay(message_ids, read=False)


class MoveTrashAjaxView(MessageUpdateView):
    """
    Move messages to trash.
    """
    def handle_message_update(self, message_ids):
        # EmailMessage.objects.filter(id__in=self.message_ids).
        pass


class EmailComposeView(FormView):
    template_name = 'messaging/email/email_compose.html'
    form_class = ComposeEmailForm
    message_object_query_args = ()
    get_email_headers = False
    remove_old_message = True

    def dispatch(self, request, *args, **kwargs):
        """
        Make sure the right handler is called for the type of request.

        :param request: The browser request tot this view.
        :param args: Arguments passed to this view.
        :param kwargs: Keyword arguments passed to this view.
        :return: An HttpResponse object.
        """
        self.message_id = kwargs.get('pk')
        if self.message_id:
            self.instance = get_object_or_404(EmailMessage, self.message_object_query_args, pk=self.message_id)
        return super(EmailComposeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Get the keyword arguments that will be used to initiate the form.

        :return: An dict of keyword arguments.
        """
        kwargs = super(EmailComposeView, self).get_form_kwargs()
        if hasattr(self, 'instance'):
            kwargs.update({
                'draft_id': self.instance.pk,
                'initial': {
                    'send_from': self.instance.from_email,
                    'subject': self.instance.subject,
                    'send_to_normal': self.instance.to_combined,
                    'send_to_cc': self.instance.to_cc_combined,
                    'send_to_bcc': self.instance.to_bcc_combined,
                }
            })
        return kwargs

    def form_valid(self, form):
        """
        Handle the form data according to the type of submit.

        :param form: The form that was validated successfully.
        :return: An HttpResponse object.
        """
        unsaved_form = form.save(commit=False)
        server = None
        
        try:
            server = LilyIMAP(provider=unsaved_form.send_from.provider, account=unsaved_form.send_from)

            # Create python email message object
            if 'submit-save' in self.request.POST or 'submit-send' in self.request.POST:
                # Generate email message source
                email_message = EmailMultiAlternatives(
                    subject=unsaved_form.subject,
                    body=unsaved_form.body_text or flatten_html_to_text(unsaved_form.body_html, replace_br=True),  # TODO Check why we need flatten_html
                    from_email=unsaved_form.send_from.email.email_address,
                    to=[unsaved_form.send_to_normal],
                    cc=[unsaved_form.send_to_cc],
                    bcc=[unsaved_form.send_to_bcc],
                    headers=self.get_email_headers() if self.get_email_headers else None,
                )
                email_message.attach_alternative(unsaved_form.body_html, 'text/html')

                # TODO support attachments

                success = True
                if 'submit-save' in self.request.POST:  # Save draft
                    success = self.save_message(server, email_message, unsaved_form)
                elif 'submit-send' in self.request.POST:  # Send draft
                    success = self.send_message(server, email_message)

                # Remove (old) drafts in every case
                if 'submit-discard' in self.request.POST or 'submit-save' in self.request.POST or 'submit-send' in self.request.POST and hasattr(self, 'instance') and success and self.remove_old_message:
                    self.remove_old_message(server)
        except Exception, e:
            log.error(traceback.format_exc(e))
        finally:
            if server:
                server.logout()

        return super(EmailComposeView, self).form_valid(form)

    def save_message(self, server, email_message, unsaved_form):
        """
        Save the message as a draft to the database and to the server via IMAP.

        :param server: The server on which the draft needs to be saved.
        :param email_message: The message that needs to be saved as a draft.
        :param unsaved_form: Successfully validated form that is not yet saved to the database.
        :return: A Boolean indicating whether the save was successful.
        """
        error = False
        message_string = unicode(email_message.message().as_string(unixfrom=False))

        try:  # Save draft remotely and sync this specific message
            uid = int(server.save_draft(message_string))
            message = server.get_modifiers_for_uid(
                uid,
                modifiers=['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE'],
                folder=DRAFTS
            )
            folder = server.get_folder_by_identifier(DRAFTS)
            save_email_messages(
                {uid: message},
                unsaved_form.send_from,
                folder.get_server_name(),
                folder.identifier,
                new_messages=True
            )

            try:
                self.new_draft = EmailMessage.objects.get(
                    account=unsaved_form.send_from,
                    uid=uid,
                    folder_name=folder.get_server_name()
                )
            except EmailMessage.DoesNotExist, e:
                log.error(traceback.format_exc(e))
        except Exception, e:
            log.error(traceback.format_exc(e))
            error = True
        finally:
            return not error  # return whether or not this function was executed successfully

    def send_message(self, server, email_message):
        """
        Send the message via IMAP and save the sent message to the database.

        :param server: The server on which the message needs to be sent.
        :param email_message: The message that needs to be sent.
        :return: A Boolean indicating whether the save was successful.
        """
        error = False
        try:
            server.get_smtp_server(fail_silently=False).send_messages([email_message])
            synchronize_folder(
                server,
                server.get_folder_by_identifier(SENT),
                criteria=['subject "%s"' % email_message.subject],
                new_only=True
            )
        except Exception, e:
            log.error(traceback.format_exc(e))
            error = True
        finally:
            return not error  # return whether or not this function was executed successfully

    def remove_old_message(self, server):
        """
        Remove old version of the message from the server and out of the database.

        :param server: The server from which the old message needs to be removed.
        """
        try:
            if self.instance.uid:
                server.delete_from_folder(
                    identifier=DRAFTS,
                    message_uids=[self.instance.uid],
                    trash_only=False
                )

            self.instance.delete()
        except Exception, e:
            log.error(traceback.format_exc(e))

    def get_email_headers(self):
        """
        Method stub for subclasses to overwrite.

        :raise: NotImplementedError, because it's only a stub.
        """
        #raise NotImplementedError('This function is not implemented. For custom headers overwrite this function.')
        return None

    def get_context_data(self, **kwargs):
        """
        Get context data that is used for the rendering of the template.

        :param kwargs: Keyword arguments.
        :return: A dict containing the context data.
        """
        context = super(EmailComposeView, self).get_context_data(**kwargs)

        # Query for all contacts which have e-mail addresses
        contacts_addresses_qs = Contact.objects.filter(
            email_addresses__in=EmailAddress.objects.all()
        ).prefetch_related('email_addresses')

        known_contact_addresses = []
        for contact in contacts_addresses_qs:
            for email_address in contact.email_addresses.all():
                contact_address = u'"%s" <%s>' % (contact.full_name(), email_address.email_address)
                known_contact_addresses.append(contact_address)

        templates = EmailTemplate.objects.all()
        template_list = {}
        for template in templates:
            template_list.update({
                template.pk: {
                    'subject': template.subject,
                    'html_part': TemplateParser(template.body_html).render(self.request),
                    'text_part': TemplateParser(template.body_text).render(self.request),
                }
            })

        context.update({
            'known_contact_addresses': simplejson.dumps(known_contact_addresses),
            'template_list': simplejson.dumps(template_list),
        })

        return context

    def get_success_url(self):
        """
        Return the appropriate success URL depending on the button pressed.

        :return: A success URL.
        """
        if 'submit-save' in self.request.POST:
            return reverse('messaging_email_compose', kwargs={'pk': self.new_draft.pk})
        elif 'submit-send' in self.request.POST:
            return reverse('messaging_email_inbox')
        elif 'submit-back' in self.request.POST or 'submit-discard' in self.request.POST:
            return reverse('messaging_email_drafts')
        else:
            return reverse('messaging_email_inbox')


class EmailCreateView(EmailComposeView):
    template_name = 'messaging/email/email_compose.html'
    form_class = ComposeEmailForm
    message_object_query_args = (Q(folder_identifier=DRAFTS.lstrip('\\')) | Q(flags__icontains='draft'))


class EmailReplyView(EmailComposeView):
    message_object_query_args = (~Q(folder_identifier=DRAFTS.lstrip('\\')) & ~Q(flags__icontains='draft'))
    get_email_headers = True
    remove_old_message = False

    def get_form_kwargs(self, **kwargs):
        keyword_arguments = super(EmailReplyView, self).get_form_kwargs(**kwargs)

        if hasattr(self, 'instance'):
            keyword_arguments['initial']['subject'] = 'Re: %s' % keyword_arguments['initial']['subject']
            keyword_arguments['initial']['send_to_normal'] = self.instance.from_combined
            keyword_arguments['message_type'] = 'reply'

        return keyword_arguments

    def get_email_headers(self):
        """
        Return reply-to e-mail header.
        """
        email_headers = {}
        if hasattr(self.message, 'send_from'):
            sender = email.utils.parseaddr(self.message.send_from)
            reply_to_name = sender[0]
            reply_to_address = sender[1]
            email_headers.update({'Reply-To': '"%s" <%s>' % (reply_to_name, reply_to_address)})
        return email_headers


class EmailForwardView(EmailReplyView):
    message_object_query_args = (~Q(folder_identifier=DRAFTS.lstrip('\\')) & ~Q(flags__icontains='draft'))
    get_email_headers = True
    remove_old_message = False

    def get_form_kwargs(self, **kwargs):
        """
        Get the keyword arguments that will be used to initiate the form.

        :return: An dict of keyword arguments.
        """
        keyword_arguments = super(EmailReplyView, self).get_form_kwargs(**kwargs)

        if hasattr(self, 'instance'):
            keyword_arguments['initial']['subject'] = 'Fwd: %s' % keyword_arguments['initial']['subject']
            keyword_arguments['message_type'] = 'forward'

        return keyword_arguments


class EmailBodyPreviewView(TemplateView):
    template_name = 'messaging/email/email_compose_frame.html'  # default for non-templated e-mails

    def dispatch(self, request, *args, **kwargs):
        self.object_id = kwargs.get('object_id', None)
        # self.message_id = kwargs.get('message_id', None)
        self.message_type = kwargs.get('message_type', None)
        self.template_id = kwargs.get('template_id', None)
        self.message = None

        if self.message_type == 'template' and self.object_id:
            self.template = get_object_or_404(
                EmailTemplate,
                pk=self.object_id
            )
        elif self.object_id:
            self.message = get_object_or_404(
                EmailMessage,
                ~Q(folder_identifier=DRAFTS.lstrip('\\')) & ~Q(flags__icontains='draft'),
                pk=self.object_id
            )

            if self.template_id:
                self.template = get_object_or_404(
                    EmailTemplate,
                    pk=self.template_id
                )

        return super(EmailBodyPreviewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(EmailBodyPreviewView, self).get_context_data(**kwargs)

        if self.message_type == 'template' and self.object_id:
            body = self.template.body_html
        elif self.object_id:
            quoted_content = self.message.indented_body

            if self.message_type == 'forward':
                notice = _('Begin forwarded message:')
            else:
                notice = _('On %s, %s wrote:' % (
                    self.message.sent_date.strftime(_('%b %e, %Y, at %H:%M')),
                    self.message.from_combined)
                )

            quoted_content = '<div>' + notice + '</div>' + quoted_content

            if hasattr(self, 'template'):
                template = TemplateParser(self.template.body_html).render(self.request) or self.template.body_text
                body = '<div>' + template + '</div>' + '<br />' * 2 + quoted_content
            else:
                signature = u''
                body = signature + '<br />' * 2 + quoted_content
        else:
            body = u''

        kwargs.update({
            'draft': body
        })

        return kwargs


    # def get_context_data(self, **kwargs):
    #     kwargs = super(EmailBodyPreviewView, self).get_context_data(**kwargs)
    #
    #     body = u''
    #
    #     # Check for existing draft
    #     if self.message:
    #         reply = u''
    #         signature = u''
    #         quoted_content = self.message.indented_body
    #
    #         # Prepend notice that the following text is a quote
    #         #
    #         # On Jan 15, 2013, at 14:45, Developer VoIPGRID <developer@voipgrid.nl> wrote:
    #         #
    #         if self.message_type == 'forward':
    #             notice = _('Begin forwarded message:')
    #         else:
    #             notice = _('On %s, %s wrote:' % (self.message.sent_date.strftime(_('%b %e, %Y, at %H:%M')), self.message.from_combined))
    #         quoted_content = '<div>' + notice + '</div>' + quoted_content
    #
    #         body = reply + signature + '<br />' * 2 + quoted_content
    #
    #     kwargs.update({
    #         # TODO get draft or user signature
    #         # 'draft': get_user_sig(),
    #         'draft': body
    #     })
    #
    #     return kwargs


class EmailConfigurationWizardTemplate(TemplateView):
    """
    View to provide html for wizard form skeleton to configure e-mail accounts.
    """
    template_name = 'messaging/email/wizard_configuration_form.html'


class EmailConfigurationView(SessionWizardView):
    template_name = 'messaging/email/wizard_configuration_form_step.html'

    def dispatch(self, request, *args, **kwargs):
        # Verify email address exists
        self.email_address_id = kwargs.get('pk')
        try:
            pk = kwargs.pop('pk')
            self.email_address = EmailAddress.objects.get(pk=pk)
        except EmailAddress.DoesNotExist:
            raise Http404()

        # Set up initial values per step
        self.initial_dict = {
            '0': {},
            '1': {},
            '2': {}
        }

        # Default: email as username
        self.initial_dict['0']['email'] = self.initial_dict['0']['username'] = self.email_address.email_address

        try:
            email_account = EmailAccount.objects.get(email=self.email_address)
        except EmailAccount.DoesNotExist:
            # Set from_name
            contacts = self.email_address.contact_set.all()
            if len(contacts) > 0:  # check to be safe, but should always have a contact when using this format
                contact = contacts[0]
                self.initial_dict['2']['name'] = contact.full_name()
        else:
            # Set provider data
            self.initial_dict['1']['imap_host'] = email_account.provider.imap_host
            self.initial_dict['1']['imap_port'] = email_account.provider.imap_port
            self.initial_dict['1']['imap_ssl'] = email_account.provider.imap_ssl
            self.initial_dict['1']['smtp_host'] = email_account.provider.smtp_host
            self.initial_dict['1']['smtp_port'] = email_account.provider.smtp_port
            self.initial_dict['1']['smtp_ssl'] = email_account.provider.smtp_ssl

            # Set from_name and signature
            self.initial_dict['2']['name'] = email_account.from_name
            self.initial_dict['2']['signature'] = email_account.signature

        return super(EmailConfigurationView, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Reset storage on first request.
        """
        self.storage.reset()
        return super(EmailConfigurationView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Override POST to validate the form first.
        """
        # Get the form for the current step
        form = self.get_form(data=self.request.POST.copy())

        # On first request, there's nothing to validate
        if self.storage.current_step is None:
            # Render the same form if it's not valid, continue otherwise
            if form.is_valid():
                return super(EmailConfigurationView, self).post(*args, **kwargs)
            return self.render(form)
        elif form.is_valid():
            self.storage.set_step_data(self.steps.current, self.process_step(form))
        else:
            return self.render(form)
        return super(EmailConfigurationView, self).post(*args, **kwargs)

    def get_form_kwargs(self, step=None):
        """
        Returns the keyword arguments for instantiating the form
        (or formset) on the given step.
        """
        kwargs = super(EmailConfigurationView, self).get_form_kwargs(step)

        if int(step) == 1:
            cleaned_data = self.get_cleaned_data_for_step(unicode(int(step) - 1))
            if cleaned_data is not None:
                kwargs.update({
                    'username': cleaned_data.get('username'),
                    'password': cleaned_data.get('password'),
                })

        return kwargs

    def done(self, form_list, **kwargs):
        data = {}
        for form in self.form_list.keys():
            data[form] = self.get_cleaned_data_for_step(form)

        # Save provider and emailaccount instances
        provider = EmailProvider()
        provider.imap_host = data['1']['imap_host']
        provider.imap_port = data['1']['imap_port']
        provider.imap_ssl = data['1']['imap_ssl']
        provider.smtp_host = data['1']['smtp_host']
        provider.smtp_port = data['1']['smtp_port']
        provider.smtp_ssl = data['1']['smtp_ssl']

        provider.save()

        try:
            account = EmailAccount.objects.get(email=self.email_address)
        except EmailAccount.DoesNotExist:
            account = EmailAccount()
            account.email = self.email_address

        account.account_type = 'email'
        account.from_name = data['2']['name']
        account.signature = data['2']['signature']
        account.username = data['0']['username']
        account.password = data['0']['password']
        account.provider = provider
        account.last_sync_date = datetime.datetime.now(tzutc()) - datetime.timedelta(days=1)
        account.save()

        # Link contact's user to emailaccount
        account.user_group.add(get_current_user())

        return HttpResponse(render_to_string(self.template_name, {'messaging_email_inbox': reverse('messaging_email_inbox')}, None))


class EmailSearchView(EmailFolderView):
    """
    ListView that parses search arguments and retrieves messages
    from all the user's email accounts.
    """
    def get(self, request, *args, **kwargs):
        """
        Parse search keys and search via IMAP.
        """
        if not any([kwargs.get('account_id', None), kwargs.get('folder', None)]):
            if not any([request.GET.get('account_id', None), request.GET.get('folder', None)]):
                raise Http404()
            if request.GET.get('account_id'):
                return redirect(reverse('messaging_email_search', kwargs={'account_id': request.GET.get('account_id', None), 'folder': request.GET.get('folder', None), 'search_key': request.GET.get('search_key', None)}))
            else:
                return redirect(reverse('messaging_email_search_all', kwargs={'folder': request.GET.get('folder', None), 'search_key': request.GET.get('search_key', None)}))

        # Look in url which account id and folder the searched is performed in
        account_id = kwargs.get('account_id', None)

        # Filter accounts from which the user has no access to
        ctype = ContentType.objects.get_for_model(EmailAccount)
        accounts_qs = request.user.messages_accounts.filter(polymorphic_ctype=ctype)
        if account_id is not None:
            accounts = [int(account_id)]
            accounts_qs = accounts_qs.filter(pk__in=accounts)

            if len(accounts_qs) == 0:  # When provided, but no matches were found raise 404
                raise Http404()

        # Get folder name from url or settle for ALLMAIL
        folder_name = kwargs.get('folder', None)
        if folder_name is None:
            self.folder = self.folder_locale_name = ALLMAIL
            self.folder_identifier = ALLMAIL
        else:
            self.folder = urllib.unquote_plus(folder_name)
            self.folder_locale_name = self.folder.split('/')[-1:][0]
            self.folder_name = self.folder_locale_name

        if len(accounts_qs) > 0:
            if len(set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set([self.folder]))) > 0:
                folder_flag = set([INBOX, SENT, DRAFTS, TRASH, SPAM]).intersection(set([self.folder])).pop()
                self.folder_name = None
                self.folder_identifier = folder_flag

                account = accounts_qs[0]
                server = None
                try:
                    server = LilyIMAP(account=account, provider=account.provider)
                    self.folder_locale_name = server.get_folder(folder_flag).get_name()
                except Exception, e:
                    print traceback.format_exc(e)
                finally:
                    if server:
                        server.logout()

        # Check if folder is from account
        folder_found = False
        for account in accounts_qs:
            for folder_name, folder in account.folders.items():
                if folder_name == self.folder_locale_name:
                    folder_found = True
                    break

                children = folder.get('children', {})
                for sub_folder_name, sub_folder in children.items():
                    if sub_folder_name == self.folder_locale_name:
                        folder_found = True
                        break

        if not folder_found:
            raise Http404()

        # Scrape messages together from one or more e-mail accounts
        search_criteria = self.parse_search_keys(kwargs.get('search_key'))
        self.imap_search_in_accounts(search_criteria, accounts=accounts_qs)

        return super(EmailSearchView, self).get(request, *args, **kwargs)

    def parse_search_keys(self, search_string):
        """
        Figure out what to search for and return an IMAP compatible search string.
        """
        TOKENS_START = ['from', 'to', 'cc', 'bcc', 'subject', 'has']
        TOKEN_END = ','
        TOKEN_VALUE_START = ':'

        def get_next_token(search_string, begin_index):
            token = None
            token_value = None

            # Find token start index
            token_start_index = next_begin_index = begin_index
            first_token_start_index = len(search_string)
            for TOKEN_START in TOKENS_START:
                try:
                    temp_token_start_index = search_string.index(TOKEN_START, begin_index)
                except ValueError:
                    continue
                else:
                    if temp_token_start_index <= first_token_start_index:
                        token_start_index = first_token_start_index = temp_token_start_index
                        token = TOKEN_START
                next_begin_index = token_start_index

            # Search for TOKEN_END preceding first_token_start_index
            try:
                token_end_index = search_string.index(TOKEN_END, begin_index, token_start_index)
            except ValueError:
                pass
            else:
                # Replace token with whatever comes next as return value
                token = None
                next_begin_index = first_token_start_index
                token_value = search_string[token_end_index:token_start_index].strip(' %s' % TOKEN_END)

            # Find token value
            if token is not None:
                # Assume start for token_value is after TOKEN_VALUE_START
                token_value_start_index = search_string.index(TOKEN_VALUE_START, token_start_index) + len(TOKEN_VALUE_START)
                # Find end of token_value by TOKEN_END or end of string
                try:
                    token_value_end_index = search_string.index(TOKEN_END, token_value_start_index - 1)
                except ValueError:
                    token_value_end_index = len(search_string)

                # Get token_value
                token_value = search_string[token_value_start_index:token_value_end_index]

                # Set next starting index after token_value
                next_begin_index = token_value_end_index
            elif token_value is None:
                # If no token was provided
                token_value = search_string[token_start_index:].strip(' %s' % TOKEN_END)
                next_begin_index = len(search_string)

            return token, token_value, next_begin_index

        criteria = []
        begin_index = 0
        token = not None
        while begin_index < len(search_string):
            token, token_value, begin_index = get_next_token(search_string, begin_index)

            # If valid token add to criteria 'as is'
            if token is not None and token_value is not None:
                criteria.append(u'%s %s' % (token.upper(), token_value))
            elif token_value is not None:
                # Add token_value as full-text
                criteria.append(u'TEXT "%s"' % token_value)

        if not any(criteria):
            criteria = 'TEXT "%s"' % search_string

        return criteria

    def imap_search_in_accounts(self, search_criteria, accounts):
        """
        Performa a search on given or all accounts and save the results.
        """
        self.resultset = []  # result set of email messages pks

        # Find corresponding messages in database and save message pks
        for account in accounts:

            server = None
            try:
                server = LilyIMAP(account=account, provider=account.provider)
                total_count, uids = server.search_in_folder(self.folder, search_criteria)

                if len(uids):
                    qs = EmailMessage.objects.none()
                    if self.folder_name is not None and self.folder_identifier is not None:
                        qs = EmailMessage.objects.filter(Q(folder_identifier=self.folder_identifier.lstrip('\\')) | Q(folder_name=self.folder_name))
                    elif self.folder_name is not None:
                        qs = EmailMessage.objects.filter(folder_name__in=[self.folder_name, self.folder])
                    elif self.folder_identifier is not None:
                        qs = EmailMessage.objects.filter(folder_identifier=self.folder_identifier.lstrip('\\'))
                    qs = qs.filter(account=account, uid__in=uids).order_by('-sent_date')

                    pks = qs.values_list('pk', flat=True)
                    self.resultset += list(pks)
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                server.logout()

    def get_queryset(self):
        """
        Return all messages matching the result set.
        """
        return EmailMessage.objects.filter(pk__in=self.resultset).order_by('-sent_date')

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to reflect the folder being searched in.
        """
        kwargs = super(EmailSearchView, self).get_context_data(**kwargs)
        kwargs.update({
            'list_title': _('%s for %s') % (self.folder_locale_name, kwargs.get('list_title'))
        })
        return kwargs


# E-mail folder views
email_inbox_view = login_required(EmailInboxView.as_view())
email_sent_view = login_required(EmailSentView.as_view())
email_drafts_view = login_required(EmailDraftsView.as_view())
email_trash_view = login_required(EmailTrashView.as_view())
email_spam_view = login_required(EmailSpamView.as_view())
email_account_folder_view = login_required(EmailFolderView.as_view())

# Ajax views
email_html_view = login_required(EmailMessageHTMLView.as_view())
email_json_view = login_required(EmailMessageJSONView.as_view())
mark_read_view = login_required(MarkReadAjaxView.as_view())
mark_unread_view = login_required(MarkUnreadAjaxView.as_view())
move_trash_view = login_required(MoveTrashAjaxView.as_view())

# E-mail interaction views
email_compose_view = login_required(EmailCreateView.as_view())
email_body_preview_view = login_required(EmailBodyPreviewView.as_view())
email_reply_view = login_required(EmailReplyView.as_view())
email_forward_view = login_required(EmailForwardView.as_view())

# E-mail account wizard views
email_configuration_wizard_template = login_required(EmailConfigurationWizardTemplate.as_view())
email_configuration_wizard = login_required(EmailConfigurationView.as_view([EmailConfigurationStep1Form, EmailConfigurationStep2Form, EmailConfigurationStep3Form]))

edit_email_account_view = login_required(EditEmailAccountView.as_view())
detail_email_account_view = login_required(DetailEmailAccountView.as_view())

# E-mail templating views
list_email_template_view = login_required(ListEmailTemplateView.as_view())
add_email_template_view = login_required(AddEmailTemplateView.as_view())
edit_email_template_view = login_required(EditEmailTemplateView.as_view())
parse_email_template_view = login_required(ParseEmailTemplateView.as_view())

# other
email_search_view = login_required(EmailSearchView.as_view())

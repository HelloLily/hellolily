import datetime
import email
import textwrap
import traceback

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from lily.contacts.models import Contact
from lily.messaging.email.emailclient import LilyIMAP, DRAFTS
from lily.messaging.email.forms import CreateUpdateEmailAccountForm, \
    CreateUpdateEmailTemplateForm, EmailTemplateFileForm, ComposeEmailForm
from lily.messaging.email.models import EmailMessage, EmailAccount, EmailTemplate
from lily.messaging.email.tasks import save_email_messages, mark_messages
from lily.messaging.email.utils import get_email_parameter_choices, flatten_html_to_text, TemplateParser
from lily.utils.models import EmailAddress
from lily.utils.views import DeleteBackAddSaveFormViewMixin


class DetailEmailInboxView(TemplateView):
    template_name = 'messaging/email/message_row.html'


class DetailEmailSentView(TemplateView):
    template_name = 'messaging/email/message_row.html'


class DetailEmailDraftView(TemplateView):
    template_name = 'messaging/email/message_row.html'


class DetailEmailArchiveView(TemplateView):
    template_name = 'messaging/email/message_row.html'


class DetailEmailComposeView(TemplateView):
    template_name = 'messaging/email/account_create.html'


class AddEmailAccountView(CreateView):
    """
    Create a new e-mail account that can be used for sending and retreiving emails.
    """
    template_name = 'messaging/email/account_create.html'
    model = EmailAccount
    form_class = CreateUpdateEmailAccountForm


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


class AddEmailTemplateView(DeleteBackAddSaveFormViewMixin, CreateView):
    """
    Create a new e-mail template that can be used for sending emails.
    """
    template_name = 'messaging/email/template_create_or_update.html'
    model = EmailTemplate
    form_class = CreateUpdateEmailTemplateForm

    def get_context_data(self, **kwargs):
        context = super(AddEmailTemplateView, self).get_context_data(**kwargs)
        context.update({
            'parameter_choices': simplejson.dumps(get_email_parameter_choices()),
        })
        return context

    def get_success_url(self):
        """
        Redirect to the edit view, so the default values of parameters can be filled in.
        """
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
        return reverse('messaging_email_inbox')


class DetailEmailTemplateView(TemplateView):
    """
    Show the details of an existing e-mail template.
    """
    template_name = 'messaging/email/account_create.html'


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


class EmailInboxView(ListView):
    """
    Show a list of e-mail messages.
    """
    template_name = 'messaging/email/model_list.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        # Check need to synchronize before hitting the database
        ctype = ContentType.objects.get_for_model(EmailAccount)
        self.messages_accounts = request.user.messages_accounts.filter(polymorphic_ctype=ctype).all()
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1

        try:
            page = int(page)
        except:
            page = 1

        self.queryset = self.get_queryset()

        return super(EmailInboxView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return EmailMessage.objects.filter(~Q(flags__icontains='draft'), account__in=self.messages_accounts).order_by('-sent_date')

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(EmailInboxView, self).get_context_data(**kwargs)
        kwargs.update({
            'list_item_template': 'messaging/email/model_list_item.html',
            'accounts': ', '.join([messaging_account.email for messaging_account in self.messages_accounts]),
        })

        return kwargs


class EmailDraftListView(EmailInboxView):
    """
    Show a list of e-mail message drafts.
    """
    def get_queryset(self):
        return EmailMessage.objects.filter(flags__icontains='draft', account__in=self.messages_accounts).order_by('-sent_date')


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

            if instance.body is None or len(instance.body.strip()) == 0:
                # Retrieve directly from IMAP (marks as read automatically)
                server = LilyIMAP(provider=instance.account.provider, account=instance.account)
                message = server.get_modifiers_for_uid(instance.uid, modifiers=['BODY[]', 'FLAGS', 'RFC822.SIZE'], folder=instance.folder_name)
                if len(message):
                    save_email_messages({instance.uid: message}, instance.account, message.get('folder_name'))

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
                'flat_body': truncatechars(instance.flatten_body, 200).encode('utf-8'),
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
            body = u''
            if instance.body:
                body = render_to_string(self.template_name, {'is_plain': instance.is_plain, 'body': instance.body.encode('utf-8')})
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

    def dispatch(self, request, *args, **kwargs):
        """
        Get message draft by pk or raise 404.
        """
        self.message_id = kwargs.get('pk')
        if self.message_id:
            try:
                # This is the message being drafted
                self.message = EmailMessage.objects.get(flags__icontains='draft', pk=self.message_id)
            except EmailMessage.DoesNotExist:
                raise Http404()

        return super(EmailComposeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        """
        Provide initial values for a draft.
        """
        kwargs = super(EmailComposeView, self).get_form_kwargs(**kwargs)
        if hasattr(self, 'message'):
            kwargs.update({
                'draft_id': self.message_id,
                'initial': {
                    'send_from': self.message.from_email,
                    'subject': self.message.subject,
                    'send_to_normal': self.message.to_combined,
                    'send_to_cc': self.message.to_cc_combined,
                    'send_to_bcc': self.message.to_bcc_combined,
                    'body': self.message.body or '',
                }
            })

        return kwargs

    def form_valid(self, form):
        """
        Check to save or send an e-mail message.
        """
        instance = form.save(commit=False)
        remove_draft = True

        # Create python email message object
        if 'submit-save' in self.request.POST or 'submit-send' in self.request.POST:
            # Prepare text version of e-mail
            text_body = flatten_html_to_text(instance.body, replace_br=True)

            # Generate email message source
            email_message = EmailMultiAlternatives(subject=instance.subject, body=text_body, from_email=instance.send_from.email, to=[instance.send_to_normal], cc=[instance.send_to_cc], bcc=[instance.send_to_bcc])
            email_message.attach_alternative(instance.body, 'text/html')

            # TODO support attachments

        # Save draft
        if 'submit-save' in self.request.POST:
            message_string = unicode(email_message.message().as_string(unixfrom=False))

            # Save draft remotely and sync this specific message
            server = None
            try:
                server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)

                uid = int(server.save_draft(message_string))
                message = server.get_modifiers_for_uid(uid, modifiers=['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE'], folder=DRAFTS)
                save_email_messages({uid: message}, instance.send_from, server.get_server_name_for_folder(DRAFTS), new_messages=True)

                try:
                    self.new_draft = EmailMessage.objects.get(account=instance.send_from, uid=uid, folder_name=server.get_server_name_for_folder(DRAFTS))
                except EmailMessage.DoesNotExist, e:
                    print traceback.format_exc(e)
            except Exception, e:
                print traceback.format_exc(e)
                remove_draft = False
            finally:
                if server:
                    server.logout()

        # Send draft
        elif 'submit-send' in self.request.POST:
            server = None
            try:
                server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)
                server.get_smtp_server(fail_silently=False).send_messages([email_message])
            except Exception, e:
                print traceback.format_exc(e)
                remove_draft = False

        # Remove (old) drafts in every case
        if 'submit-discard' in self.request.POST or 'submit-save' in self.request.POST or 'submit-send' in self.request.POST:
            if self.message_id and remove_draft:
                server = None
                try:
                    server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)
                    if self.message.uid:
                        # remove remotely
                        server.delete_from_folder(identifier=DRAFTS, message_uids=[self.message.uid], trash_only=False)

                    if self.message.pk:
                        # remote locally
                        self.message.delete()
                except Exception, e:
                    print traceback.format_exc(e)
                finally:
                    if server:
                        server.logout()

        return super(EmailComposeView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Allow autocomplete for email addresses.
        """
        kwargs = super(EmailComposeView, self).get_context_data(**kwargs)

        # Query for all contacts which have e-mail addresses
        contacts_addresses_qs = Contact.objects.filter(email_addresses__in=EmailAddress.objects.all()).prefetch_related('email_addresses')

        known_contact_addresses = []
        for contact in contacts_addresses_qs:
            for email_address in contact.email_addresses.all():
                contact_address = u'"%s" <%s>' % (contact.full_name(), email_address.email_address)
                known_contact_addresses.append(contact_address)

        kwargs.update({
            'known_contact_addresses': simplejson.dumps(known_contact_addresses),
        })

        return kwargs

    def get_success_url(self):
        """
        Return different URLs depending on the button pressed.
        """
        # Redirect to url with draft id
        if 'submit-save' in self.request.POST:
            return reverse('messaging_email_compose', kwargs={'pk': self.new_draft.pk})

        if 'submit-send' in self.request.POST:
            return reverse('messaging_email_inbox')

        if 'submit-back' in self.request.POST or 'submit-discard' in self.request.POST:
            return reverse('messaging_email_drafts')

        return reverse('messaging_email_inbox')


class EmailReplyView(FormView):
    template_name = 'messaging/email/email_compose.html'
    form_class = ComposeEmailForm

    def dispatch(self, request, *args, **kwargs):
        """
        Get message being replied to or raise 404.
        """
        self.message_id = kwargs.get('pk')
        if self.message_id:
            try:
                # This is the message being replied to
                self.message = EmailMessage.objects.get(~Q(flags__icontains='draft'), pk=self.message_id)
            except EmailMessage.DoesNotExist:
                raise Http404()

        return super(EmailReplyView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        """
        Build initial value for the e-mail body.
        """
        # Body exists of reply, signature and original content
        reply = u''
        signature = u''  # get_user_signature()
        quoted_content = self.message.body or ''

        if len(quoted_content) > 0:
            content_type_header = self.message.headers.filter(name='Content-Type')
            if len(content_type_header) > 0:
                content_type = content_type_header[0].value.split(';')[0]
                if 'text/plain' in content_type:
                    # In case of plain text, make quoted text appear like
                    #
                    # > This is the
                    # > original e-mail
                    # > content.
                    quoted_lines = textwrap.wrap(quoted_content, 80)
                    quoted_lines = ['> %s' % line for line in quoted_lines]
                    quoted_content = '<br />'.join(quoted_lines)

        # Prepend separation notice
        #
        # On Jan 15, 2013, at 14:45, Developer VoIPGRID <developer@voipgrid.nl> wrote:
        #
        notice = _('On %s, %s wrote:' % (self.message.sent_date.strftime(_('%b %e, %Y, at %H:%M')), self.message.from_combined))
        quoted_content = '<br />'.join([notice, quoted_content])

        body = reply + signature + '<br />' * 2 + quoted_content

        kwargs = super(EmailReplyView, self).get_form_kwargs(**kwargs)
        if hasattr(self, 'message'):
            # Set initial values
            kwargs.update({
                # 'draft_id': self.message_id,
                'initial': {
                    'subject': 'RE: %s' % self.message.subject,
                    'send_to_normal': self.message.from_combined,
                    'send_to_cc': self.message.to_cc_combined,
                    'send_to_bcc': self.message.to_bcc_combined,
                    'body': body,
                }
            })

        return kwargs

    def form_valid(self, form):
        """
        Check to save or send an e-mail message.
        """
        instance = form.save(commit=False)

        # Create python email message object
        if 'submit-save' in self.request.POST or 'submit-send' in self.request.POST:
            # Prepare text version of e-mail
            text_body = flatten_html_to_text(instance.body, replace_br=True)

            # Generate email message source
            email_message = EmailMultiAlternatives(subject=instance.subject, body=text_body, from_email=instance.send_from.email, to=[instance.send_to_normal], cc=[instance.send_to_cc], bcc=[instance.send_to_bcc], headers=self.get_email_headers())
            email_message.attach_alternative(instance.body, 'text/html')

            # TODO support attachments

        # Create draft
        if 'submit-save' in self.request.POST:
            message_string = unicode(email_message.message().as_string(unixfrom=False))

            # Save draft remotely and sync this specific message
            server = None
            try:
                server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)

                uid = int(server.save_draft(message_string))
                message = server.get_modifiers_for_uid(uid, modifiers=['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE'], folder=DRAFTS)
                save_email_messages({uid: message}, instance.send_from, server.get_server_name_for_folder(DRAFTS), new_messages=True)

                try:
                    self.new_draft = EmailMessage.objects.get(account=instance.send_from, uid=uid, folder_name=server.get_server_name_for_folder(DRAFTS))
                except EmailMessage.DoesNotExist, e:
                    print traceback.format_exc(e)
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                if server:
                    server.logout()

        # Send reply
        elif 'submit-send' in self.request.POST:
            server = None
            try:
                server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)
                server.get_smtp_server(fail_silently=False).send_messages([email_message])
            except Exception, e:
                print traceback.format_exc(e)

        return super(EmailReplyView, self).form_valid(form)

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

    def get_context_data(self, **kwargs):
        """
        Allow autocomplete for email addresses.
        """
        kwargs = super(EmailReplyView, self).get_context_data(**kwargs)

        # Query for all contacts which have e-mail addresses
        contacts_addresses_qs = Contact.objects.filter(email_addresses__in=EmailAddress.objects.all()).prefetch_related('email_addresses')

        known_contact_addresses = []
        for contact in contacts_addresses_qs:
            for email_address in contact.email_addresses.all():
                contact_address = u'"%s" <%s>' % (contact.full_name(), email_address.email_address)
                known_contact_addresses.append(contact_address)

        kwargs.update({
            'known_contact_addresses': simplejson.dumps(known_contact_addresses),
        })

        return kwargs

    def get_success_url(self):
        """
        Return different URLs depending on the button pressed.
        """
        # Redirect to url with draft id
        if 'submit-save' in self.request.POST:
            return reverse('messaging_email_compose', kwargs={'pk': self.new_draft.pk})

        if 'submit-send' in self.request.POST:
            return reverse('messaging_email_inbox')

        if 'submit-back' in self.request.POST or 'submit-discard' in self.request.POST:
            return reverse('messaging_email_drafts')

        return reverse('messaging_email_inbox')


class EmailForwardView(EmailReplyView):
    """
    Forward an e-mail message.
    """
    def get_form_kwargs(self, **kwargs):
        """
        Change kwargs generated by super()
        """
        kwargs = super(EmailForwardView, self).get_form_kwargs(**kwargs)
        if hasattr(self, 'message'):
            # Override initial values
            if 'initial' in kwargs:
                kwargs['initial'].update({
                    'subject': 'FWD: %s' % self.message.subject,
                    'send_to_normal': None,
                    'send_to_cc': None,
                    'send_to_bcc': None,
                })
        return kwargs


class EmailDraftTemplateView(TemplateView):
    template_name = 'messaging/email/email_compose_frame.html'  # default for non-templated e-mails

    def dispatch(self, request, *args, **kwargs):
        self.message_id = kwargs.get('pk')

        return super(EmailDraftTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(EmailDraftTemplateView, self).get_context_data(**kwargs)

        if self.message_id:
            try:
                self.message = EmailMessage.objects.get(flags__icontains='draft', pk=self.message_id)
            except EmailMessage.DoesNotExist:
                raise Http404()

        body = u''

        # Check for existing draft
        if self.message_id:
            body = self.message.body

        if not len(body.strip('</>brdiv ')):
            # Get user's signature
            # get_user_sig()
            pass

        kwargs.update({
            # TODO get draft or user signature
            # 'draft': get_user_sig(),
            'draft': body
        })

        return kwargs


# E-mail views
# detail_email_inbox_view = DetailEmailInboxView.as_view()
email_inbox_view = login_required(EmailInboxView.as_view())
email_drafts_view = login_required(EmailDraftListView.as_view())
email_html_view = login_required(EmailMessageHTMLView.as_view())
email_json_view = login_required(EmailMessageJSONView.as_view())
mark_read_view = login_required(MarkReadAjaxView.as_view())
mark_unread_view = login_required(MarkUnreadAjaxView.as_view())
move_trash_view = login_required(MoveTrashAjaxView.as_view())

email_compose_view = login_required(EmailComposeView.as_view())
email_compose_template_view = login_required(EmailDraftTemplateView.as_view())
email_reply_view = login_required(EmailReplyView.as_view())
email_forward_view = login_required(EmailForwardView.as_view())

detail_email_sent_view = DetailEmailSentView.as_view()
detail_email_draft_view = DetailEmailDraftView.as_view()
detail_email_archive_view = DetailEmailArchiveView.as_view()
detail_email_compose_view = DetailEmailComposeView.as_view()

# E-mail account views
add_email_account_view = AddEmailAccountView.as_view()
edit_email_account_view = EditEmailAccountView.as_view()
detail_email_account_view = DetailEmailAccountView.as_view()

# E-mail template views
add_email_template_view = AddEmailTemplateView.as_view()
edit_email_template_view = EditEmailTemplateView.as_view()
detail_email_template_view = DetailEmailTemplateView.as_view()
parse_email_template_view = ParseEmailTemplateView.as_view()

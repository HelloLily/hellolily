import datetime
import traceback

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from lily.contacts.models import Contact
from lily.messages.email.emailclient import LilyIMAP, DRAFTS
from lily.messages.email.forms import CreateUpdateEmailAccountForm, \
 CreateUpdateEmailTemplateForm, EmailTemplateFileForm, ComposeEmailForm
from lily.messages.email.models import EmailMessage, EmailAccount, EmailTemplate
from lily.messages.email.tasks import save_email_messages, mark_messages
from lily.messages.email.utils import get_email_parameter_choices, flatten_html_to_text
from lily.utils.models import EmailAddress


class DetailEmailInboxView(TemplateView):
    template_name = 'messages/email/message_row.html'


class DetailEmailSentView(TemplateView):
    template_name = 'messages/email/message_row.html'


class DetailEmailDraftView(TemplateView):
    template_name = 'messages/email/message_row.html'


class DetailEmailArchiveView(TemplateView):
    template_name = 'messages/email/message_row.html'


class DetailEmailComposeView(TemplateView):
    template_name = 'messages/email/account_create.html'


class AddEmailAccountView(CreateView):
    """
    Create a new e-mail account that can be used for sending and retreiving emails.
    """
    template_name = 'messages/email/account_create.html'
    model = EmailAccount
    form_class = CreateUpdateEmailAccountForm


class EditEmailAccountView(TemplateView):
    """
    Edit an existing e-mail account.
    """
    template_name = 'messages/email/account_create.html'


class DetailEmailAccountView(TemplateView):
    """
    Show the details of an existing e-mail account.
    """
    template_name = 'messages/email/account_create.html'


class AddEmailTemplateView(CreateView):
    """
    Create a new e-mail template that can be used for sending emails.
    """
    template_name = 'messages/email/template_create_or_update.html'
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
        return reverse('messages_email_template_edit', kwargs={
            'pk': self.object.pk,
        })


class EditEmailTemplateView(UpdateView):
    """
    Parse an uploaded template for variables and return a generated form/
    """
    template_name = 'messages/email/template_create_or_update.html'
    model = EmailTemplate
    form_class = CreateUpdateEmailTemplateForm


class DetailEmailTemplateView(TemplateView):
    """
    Show the details of an existing e-mail template.
    """
    template_name = 'messages/email/account_create.html'


class ParseEmailTemplateView(FormView):
    """
    Parse an uploaded template for variables and return a generated form
    """
    template_name = 'messages/email/template_create_or_update_base_form.html'
    form_class = EmailTemplateFileForm

    def form_valid(self, form):
        """
        Return parsed form with rendered parameter fields
        """
        # we return content of the file here because this easily enables us to do more sophisticated parsing in the future.
        body_file = form.cleaned_data.get('body_file')

        response_dict = {
            'valid': True,
        }

        response_dict.update(TemplateFileParser(body_file, context={
            'account_name': 'test',
        }).parse())


        return HttpResponse(simplejson.dumps(response_dict), mimetype="application/json")


    def form_invalid(self, form):
        return HttpResponse(simplejson.dumps({
            'valid': False,
            'errors': form.errors,
        }), mimetype="application/json")


class EmailInboxView(ListView):
    """
    Show a list of e-mail messages.
    """
    template_name = 'messages/email/model_list.html'
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
            'list_item_template': 'messages/email/model_list_item.html',
            'accounts': ', '.join([message_account.email for message_account in self.messages_accounts]),
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
    template_name = 'messages/email/email_heading.html'

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

            message = {}
            message['id'] = instance.id
            message['sent_date'] = unix_time_millis(instance.sent_date)
            message['flags'] = instance.flags
            message['uid'] = instance.uid
            message['flat_body'] = truncatechars(instance.flat_body, 200).encode('utf-8')
            message['subject'] = instance.subject.encode('utf-8')
            message['size'] = instance.size
            message['is_private'] = instance.is_private
            message['is_read'] = instance.is_seen
            message['is_plain'] = instance.is_plain
            message['folder_name'] = instance.folder_name

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
    template_name = 'messages/email/email_body.html'

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
    template_name = 'messages/email/email_compose.html'
    form_class = ComposeEmailForm

    def dispatch(self, request, *args, **kwargs):
        self.draft_id = kwargs.get('pk')

        if self.draft_id:
            try:
                self.draft = EmailMessage.objects.get(flags__icontains='draft', pk=self.draft_id)
            except EmailMessage.DoesNotExist:
                raise Http404()

        return super(EmailComposeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        # Set initial values

        kwargs = super(EmailComposeView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'draft_id': self.draft_id,
            'initial': {
                'send_from': self.draft.from_email,
                'subject': self.draft.subject,
                'send_to_normal': self.draft.to_email,
                'send_to_cc': ', '.join(self.draft.headers.filter(name='cc', ).values_list('value', flat=True)),
                'send_to_bcc': ', '.join(self.draft.headers.filter(name='bcc', ).values_list('value', flat=True)),
            }
        })

        return kwargs

    def form_valid(self, form):
        """
        Check to save or sent an e-mail message.
        """
        instance = form.save(commit=False)

        if 'submit-save' in self.request.POST:
            # Prepare text version of e-mail
            text_body = flatten_html_to_text(instance.body)

            # Generate email message source
            email_message = EmailMultiAlternatives(subject=instance.subject, body=text_body, from_email=instance.send_from.email, to=[instance.send_to_normal], cc=[instance.send_to_cc], bcc=[instance.send_to_bcc])
            email_message.attach_alternative(instance.body, 'text/html')
            message_string = unicode(email_message.message().as_string(unixfrom=False))

            # TODO support attachments

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

            # TODO redirect after submit to compose with new id in url

        elif 'submit-send' in self.request.POST:
            # send e-mail (smtp)
            # server.get_smtp_server().send_email(message_string) ?

            # remove as draft
            pass

        if 'submit-discard' in self.request.POST or 'submit-save' in self.request.POST or 'submit-send' in self.request.POST:
            server = None
            try:
                server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)
                if self.draft.uid:
                    # remove remotely
                    server.delete_from_folder(identifier=DRAFTS, message_uids=[self.draft.uid], trash_only=False)

                if self.draft.pk:
                    # remote locally
                    self.draft.delete()
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
        Return to inbox after sending e-mail.
        """

        # Redirect to url with draft id
        if 'submit-save' in self.request.POST:
            return reverse('messages_email_compose', kwargs={'pk': self.new_draft.pk})

        if 'submit-send' in self.request.POST:
            return reverse('messages_email_inbox')

        if 'submit-back' in self.request.POST:
            return reverse('messages_email_drafts')

        return reverse('messages_email_inbox')


class EmailDraftTemplateView(TemplateView):
    template_name = 'messages/email/email_compose_frame.html'  # default for non-templated e-mails

    def dispatch(self, request, *args, **kwargs):
        self.draft_id = kwargs.get('pk')

        return super(EmailDraftTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(EmailDraftTemplateView, self).get_context_data(**kwargs)

        if self.draft_id:
            try:
                self.draft = EmailMessage.objects.get(flags__icontains='draft', pk=self.draft_id)
            except EmailMessage.DoesNotExist:
                raise Http404()

        body = u''

        # Check for existing draft
        if self.draft_id:
            body = self.draft.body

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

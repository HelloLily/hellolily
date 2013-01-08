import anyjson
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from lily.contacts.models import Contact
from lily.messages.email.emailclient import LilyIMAP
from lily.messages.email.models import EmailMessage, EmailAccount, EmailTemplate
from lily.messages.email.tasks import save_email_messages, mark_messages
from lily.messages.email.forms import CreateUpdateEmailAccountForm, \
 CreateUpdateEmailTemplateForm, EmailTemplateFileForm, ComposeEmailForm
from lily.messages.email.utils import get_email_parameter_dict, get_param_vals, get_email_parameter_choices, flatten_html_to_text
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


class TempTestClass:
    def __init__(self, html=None, text=None):
        self.html = html
        self.text = text

class AddEmailTemplateView(CreateView):
    """
    Create a new e-mail template that can be used for sending emails.
    """
    template_name = 'messages/email/template_create_or_update.html'
    model = EmailTemplate
    form_class = CreateUpdateEmailTemplateForm

    def get_context_data(self, **kwargs):
        context = super(AddEmailTemplateView, self).get_context_data(**kwargs)

        # add context to template for parameter inserter javascript
#        print get_email_parameter_choices()

        return context


    def form_invalid(self, form):
        lst =  get_email_parameter_dict()

        fake_template_object = TempTestClass(
            html = form.data.get('body_html'),
            text = form.data.get('body_text')
        )

        param_list = get_param_vals(self.request, fake_template_object)

        return super(AddEmailTemplateView, self).form_invalid(form)

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
    Parse an uploaded template for variables and return a generated form/
    """
    template_name = 'messages/email/template_create_or_update_base_form.html'
    form_class = EmailTemplateFileForm

    def form_valid(self, form):
        """
        Return parsed form with rendered parameter fields
        """
        body_file = form.cleaned_data.get('body_file').read()

        return HttpResponse(anyjson.dumps({
            'valid': True,
            'html': '',
            'text': '',
        }), mimetype="application/json")

    def form_invalid(self, form):
        return HttpResponse(anyjson.dumps({
            'valid': False,
            'errors': form.errors,
        }), mimetype="application/json")


class ListEmailView(ListView):
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

        self.queryset = EmailMessage.objects.filter(account__in=self.messages_accounts).order_by('-sent_date')

        return super(ListEmailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Overloading super().get_context_data to provide the list item template.
        """
        kwargs = super(ListEmailView, self).get_context_data(**kwargs)
        kwargs.update({
            'list_item_template': 'messages/email/model_list_item.html',
            'accounts': ', '.join([message_account.email for message_account in self.messages_accounts]),
        })

        return kwargs


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
        raise NotImplementedError("Implement by sublcassing MessageUpdateView")


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

    def form_valid(self, form):
        """
        Check to save or sent an e-mail message.
        """
        sucess_url = super(EmailComposeView, self).form_valid(form)
        instance = form.save(commit=False)

        if 'submit-save' in self.request.POST:
            # Prepare text version of e-mail
            text_body = flatten_html_to_text(instance.body)

            # Generate email message source
            email_message = EmailMultiAlternatives(subject=instance.subject, body=text_body, from_email=instance.send_from.email, to=[instance.send_to_normal], cc=[instance.send_to_cc], bcc=[instance.send_to_bcc])
            email_message.attach_alternative(instance.body, 'text/html')
            message_string = unicode(email_message.message())

            # TODO: support attachments

            # Save draft
            server = LilyIMAP(provider=instance.send_from.provider, account=instance.send_from)
            server.save_draft(message_string)
        elif 'submit-send' in self.request.POST:
            # send e-mail (smtp)
            # server.get_smtp_server().send_email(message_string) ?
            pass

        if 'submit-discard' in self.request.POST or 'submit-sent' in self.request.POST:
            if instance.uid:
            # if instance.email_message:
                # remove remotely
                pass

            if instance.pk:
                # remote locally
                instance.remove()
            pass

        return sucess_url

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
            'known_contact_addresses': simplejson.dumps(known_contact_addresses)
        })

        return kwargs

    def get_success_url(self):
        """
        Return to inbox after sending e-mail.
        """
        return reverse('messages_email_inbox')


class EmailDraftTemplateView(TemplateView):
    template_name = 'messages/email/email_compose_frame.html'  # default for non-templated e-mails

    def get_context_data(self, **kwargs):
        kwargs = super(EmailDraftTemplateView, self).get_context_data(**kwargs)
        kwargs.update({
            # TODO get draft or user signature
            # 'draft': get_user_sig(),
        })

        return kwargs


# E-mail views
# detail_email_inbox_view = DetailEmailInboxView.as_view()
email_inbox_view = login_required(ListEmailView.as_view())
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

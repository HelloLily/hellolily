import anyjson
import datetime

from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import truncatechars
from django.utils import simplejson

from lily.messages.email.emailclient import LilyIMAP
from lily.messages.email.models import EmailMessage, EmailAccount, EmailTemplate
from lily.messages.email.tasks import get_unread_emails, save_email_messages
from lily.messages.email.forms import CreateUpdateEmailAccountForm, CreateUpdateEmailTemplateForm, EmailTemplateFileForm
from lily.messages.email.utils import get_email_parameter_dict, get_param_vals, get_email_parameter_choices, TemplateFileParser


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
            'parameter_choices': anyjson.dumps(get_email_parameter_choices()),
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


        return HttpResponse(anyjson.dumps(response_dict), mimetype="application/json")


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
        get_unread_emails(self.messages_accounts)

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
            instance = EmailMessage.objects.get(id=kwargs.get('id'))

            # See if the user has access to this message
            if instance.account not in self.messages_accounts:
                raise Http404()

            server = LilyIMAP(provider=instance.account.provider, account=instance.account)

            if instance.body is None or len(instance.body.strip()) == 0:
                # Retrieve directly from IMAP
                message = server.get_modifiers_for_uid(instance.uid, modifiers=['BODY[]', 'FLAGS', 'RFC822.SIZE'], folder=instance.folder_name)
                if len(message):
                    save_email_messages({instance.uid: message}, instance.account, message.get('folder_name'))

                instance = EmailMessage.objects.get(id=kwargs.get('id'))
            else:
                # Mark as read manually
                if server._server.folder_exists(instance.folder_name):
                    server._server.select_folder(instance.folder_name)
                    server.mark_as_read(instance.uid)
                    server._server.close_folder()

            instance.is_seen = True
            instance.save()

            message = {}
            message['id'] = instance.id
            message['sent_date'] = unix_time_millis(instance.sent_date)
            message['flags'] = instance.flags
            message['uid'] = instance.uid
            message['body'] = instance.body.encode('utf-8')
            message['flat_body'] = truncatechars(instance.flat_body, 200).encode('utf-8')
            message['size'] = instance.size
            message['is_private'] = instance.is_private
            message['is_read'] = instance.is_seen
            message['is_plain'] = instance.is_plain
            message['folder_name'] = instance.folder_name

            return HttpResponse(simplejson.dumps(message), mimetype='application/json; charset=utf-8')
        except EmailMessage.DoesNotExist:
            raise Http404()
        finally:
            if server:
                server._server.logout()


# E-mail views
# detail_email_inbox_view = DetailEmailInboxView.as_view()
email_inbox_view = login_required(ListEmailView.as_view())
email_json_view = login_required(EmailMessageJSONView.as_view())

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

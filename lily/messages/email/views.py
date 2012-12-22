import anyjson
from collections import OrderedDict

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from lily.messages.email.forms import CreateUpdateEmailAccountForm, CreateUpdateEmailTemplateForm, EmailTemplateFileForm
from lily.messages.email.models import EmailAccount, EmailTemplate
from lily.messages.email.utils import get_email_parameter_dict, get_param_vals, get_email_parameter_choices


class CreateTestDataView(TemplateView):
    template_name = 'messages/email/message_row.html'


    def get_context_data(self, **kwargs):
        context = super(CreateTestDataView, self).get_context_data(**kwargs)

#        provider, created = EmailProvider.objects.get_or_create(
#            retrieve_host='imap.gmail.com',
#            retrieve_port=993,
#            send_host='smtp.gmail.com',
#            send_port=587,
#            send_use_tls=True
#        )
#
#        account, created = EmailAccount.objects.get_or_create(
#            provider=provider,
#            name='lily email',
#            email='lily@hellolily.com',
#            username='lily@hellolily.com',
#            password='0$mxsq=3ouhr)_iz710dj!*2$vkz'
#        )
#
#        email, created = EmailMessage.objects.get_or_create(
#            account=account,
#            uid=1,
#            datetime=datetime.now(),
#            from_string='Allard Stijnman <a.g.stijnman@gmail.com>',
#            from_email='a.g.stijnman@gmail.com',
#            from_name='Allard Stijnman',
#            content_type='plaintext'
#        )

        return context


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
        print get_email_parameter_choices()

        return context


    def form_invalid(self, form):
#        lst =  get_email_parameter_dict()
#
#        fake_template_object = TempTestClass(
#            html = form.data.get('body_html'),
#            text = form.data.get('body_text')
#        )
#
#        param_list = get_param_vals(self.request, fake_template_object)

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



# Testing views
create_test_data_view = CreateTestDataView.as_view()

# E-mail views
detail_email_inbox_view = DetailEmailInboxView.as_view()
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
# Python imports
from collections import OrderedDict
import anyjson
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
import re

# Django imports
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView

# Lily imports
from lily.messages.email.forms import CreateUpdateEmailAccountForm, CreateUpdateEmailTemplateForm, TemplateParameterForm, TemplateParameterParseForm
from lily.messages.email.models import EmailAccount, EmailTemplate, EmailTemplateParameter, EmailTemplateParameterChoice
from lily.messages.email.utils import parse


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


class AddEmailTemplateView(CreateView):
    """
    Create a new e-mail template that can be used for sending emails.
    """
    template_name = 'messages/email/template_create_or_update.html'
    model = EmailTemplate
    form_class = CreateUpdateEmailTemplateForm


    def post(self, request, *args, **kwargs):
        # Fields that we know should be in the post parameters
        known_fields = ['name', 'body', 'csrfmiddlewaretoken', 'submit-add']
        # Keys of the post parameters
        post_keys = set(request.POST.keys())
        # Filter keys of known fields
        # Exclude keys ending with _select, which are added in the form, unless actual template var ends with select
        parameter_list = [x for x in post_keys if x not in known_fields and (not x.endswith('_select') or x.endswith('select_select'))]

        for index, param in enumerate(parameter_list):
            # If any of the keys ends with double select, trim the last select
            if parameter_list[index].endswith('select_select'):
                parameter_list[index] = parameter_list[index][:-7]

        self.parameter_list = parameter_list

        return super(AddEmailTemplateView, self).post(request, *args, **kwargs)


    def get_form_kwargs(self):
        kwargs =  super(AddEmailTemplateView, self).get_form_kwargs()
        if hasattr(self, 'parameter_list'):
            kwargs.update({
                'parameters': self.parameter_list,
            })

        return kwargs


    def form_valid(self, form):
        success_url = super(AddEmailTemplateView, self).form_valid(form)

        for parameter in form.parameter_list:
            label = form.cleaned_data.get('%s_select' % parameter)
            if label:
                # select value != empty so we look for value in db
                choice = EmailTemplateParameterChoice.objects.get(label='%s' % label)
                EmailTemplateParameter.objects.create(
                    template=self.object,
                    name=parameter,
                    value=choice.value,
                    label=choice.label,
                    is_dynamic=choice.is_dynamic
                )
            else:
                EmailTemplateParameter.objects.create(
                    template=self.object,
                    name=parameter,
                    value=form.cleaned_data.get(parameter),
                    label='',
                    is_dynamic=False
                )

        return success_url


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


    def get_form_kwargs(self):
        kwargs = super(EditEmailTemplateView, self).get_form_kwargs()
        self.parameter_list = EmailTemplateParameter.objects.filter(template=self.object).order_by('pk')

        parameters = OrderedDict()
        for param in self.parameter_list:
            parameters['%s' % param.name] = param.value

        kwargs.update({
            'parameters': self.parameter_list,
        })

        return kwargs

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
    form_class = TemplateParameterParseForm
    param_form_class = TemplateParameterForm

    def form_valid(self, form):
        """
        Return parsed form with rendered parameter fields
        """
        body = form.cleaned_data.get('body').read()
        parameter_list = parse(body)

        return HttpResponse(anyjson.dumps({
            'valid': True,
            'html': render_to_string(self.template_name, {
                'form': self.param_form_class(parameters=parameter_list, **self.get_form_kwargs())
            }, context_instance=RequestContext(self.request))
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
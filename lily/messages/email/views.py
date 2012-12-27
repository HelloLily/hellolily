import anyjson
import datetime
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.template.defaultfilters import truncatechars
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.list import ListView

from lily.messages.email.emailclient import LilyIMAP
from lily.messages.email.forms import CreateUpdateEmailAccountForm, CreateUpdateEmailTemplateForm, TemplateParameterForm, TemplateParameterParseForm
from lily.messages.email.models import EmailAccount, EmailTemplate, EmailMessage, EmailTemplateParameters, EmailTemplateParameterChoice
from lily.messages.email.tasks import save_email_messages, mark_messages
from lily.messages.email.utils import parse


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
        kwargs = super(AddEmailTemplateView, self).get_form_kwargs()
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
                EmailTemplateParameters.objects.create(
                    template=self.object,
                    name=parameter,
                    value=choice.value,
                    label=choice.label,
                    is_dynamic=choice.is_dynamic
                )
            else:
                EmailTemplateParameters.objects.create(
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
        self.parameter_list = EmailTemplateParameters.objects.filter(template=self.object).order_by('pk')

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


# E-mail views
# detail_email_inbox_view = DetailEmailInboxView.as_view()
email_inbox_view = login_required(ListEmailView.as_view())
email_html_view = login_required(EmailMessageHTMLView.as_view())
email_json_view = login_required(EmailMessageJSONView.as_view())
mark_read_view = login_required(MarkReadAjaxView.as_view())
mark_unread_view = login_required(MarkUnreadAjaxView.as_view())
move_trash_view = login_required(MoveTrashAjaxView.as_view())

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

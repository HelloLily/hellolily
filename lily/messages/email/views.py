# Python imports
from datetime import datetime

# Django imports
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

# Lily imports
from lily.messages.email.forms import CreateAccountForm
from lily.messages.email.models import EmailProvider, EmailAccount, EmailMessage


class CreateTestDataView(TemplateView):
    template_name = 'messages/email/message_row.html'


    def get_context_data(self, **kwargs):
        context = super(CreateTestDataView, self).get_context_data(**kwargs)

        provider, created = EmailProvider.objects.get_or_create(
            retrieve_host='imap.gmail.com',
            retrieve_port=993,
            send_host='smtp.gmail.com',
            send_port=587,
            send_use_tls=True
        )

        account, created = EmailAccount.objects.get_or_create(
            provider=provider,
            name='lily email',
            email='lily@hellolily.com',
            username='lily@hellolily.com',
            password='0$mxsq=3ouhr)_iz710dj!*2$vkz'
        )

        email, created = EmailMessage.objects.get_or_create(
            account=account,
            uid=1,
            datetime=datetime.now(),
            from_string='Allard Stijnman <a.g.stijnman@gmail.com>',
            from_email='a.g.stijnman@gmail.com',
            from_name='Allard Stijnman',
            content_type='plaintext'
        )

        return context


class EmailInboxView(TemplateView):
    template_name = 'messages/email/message_row.html'


class EmailSentView(TemplateView):
    template_name = 'messages/email/message_row.html'


class EmailDraftView(TemplateView):
    template_name = 'messages/email/message_row.html'


class EmailArchiveView(TemplateView):
    template_name = 'messages/email/message_row.html'


class CreateEmailAccountView(CreateView):
    template_name = 'messages/email/create_account.html'
    model = EmailAccount
    form_class = CreateAccountForm


create_test_data_view = CreateTestDataView.as_view()
email_inbox_view = EmailInboxView.as_view()
email_sent_view = EmailSentView.as_view()
email_draft_view = EmailDraftView.as_view()
email_archive_view = EmailArchiveView.as_view()
create_email_account_view = CreateEmailAccountView.as_view()
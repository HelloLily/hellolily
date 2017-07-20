from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from oauth2client.client import FlowExchangeError

from email_wrapper_lib.models import EmailAccount
from email_wrapper_lib.providers import registry
from email_wrapper_lib.tasks import first_sync


class AddAccountView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        provider_name = kwargs.get('provider_name')

        if provider_name in registry:
            provider = registry[provider_name]
            url = provider.flow.step1_get_authorize_url()
        else:
            messages.add_message(self.request, messages.ERROR, 'Could not redirect to validate your account.')
            url = reverse('inbox')

        return url


class AddAccountCallbackView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        provider_name = kwargs.get('provider_name')
        url = reverse('base_view')

        if provider_name in registry:
            code = self.request.GET.get('code')
            provider = registry[provider_name]

            try:
                account = EmailAccount.create_account_from_code(provider=provider, code=code)
                first_sync.delay(account.pk)
                messages.add_message(self.request, messages.SUCCESS, '{0} was created.'.format(account.username))
            except FlowExchangeError:
                messages.add_message(self.request, messages.ERROR, 'Could not get credentials for your account.')
        else:
            messages.add_message(self.request, messages.ERROR, 'Invalid callback, could not process your account.')

        return url

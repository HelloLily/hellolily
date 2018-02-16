from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, RedirectView
from oauth2client.client import FlowExchangeError

from email_wrapper_lib.conf import settings
from email_wrapper_lib.providers import registry
from .models import EmailAccount
from email_wrapper_lib.storage import Storage
from lily.utils.views import LoginRequiredMixin


class TestView(View):
    def get(self, request, *args, **kwargs):
        account_list = EmailAccount.objects.all()

        for account in account_list:
            account.manager.sync()

        return HttpResponse('test')


class AddAccountView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        provider_name = kwargs.get('provider_name')

        # TODO: maybe we do need to use requests-oauthlib for obtaining credentials, it felt more secure.
        # we could pour the raw token into oauth2client.OAuth2Credentials, which is wat is returned by step 2 below.

        # TODO: add a state in the request to prevent csrf.

        if provider_name in registry:
            provider = registry[provider_name]
            url = provider.flow.step1_get_authorize_url()
        else:
            messages.add_message(self.request, messages.ERROR, 'Could not redirect to validate your account.')
            url = reverse('inbox')

        return url


class AddAccountCallbackView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        code = request.GET.get('code')
        provider_name = kwargs.get('provider_name')
        state_valid = self.is_state_valid()

        if code and state_valid and provider_name in registry:
            # We have a code and the provider is in the registry.
            try:
                account = self.save_account(provider_name, code)
            except FlowExchangeError:
                messages.add_message(request, messages.ERROR, 'Could not get credentials for your account.')
                return HttpResponseRedirect(url)

            # Start syncing the account in the background.
            account.manager.sync()

            messages.add_message(request, messages.SUCCESS, '{0} was created.'.format(account.username))
        else:
            messages.add_message(request, messages.ERROR, 'Invalid callback, could not process your account.')

        return HttpResponseRedirect(url)

    def get_redirect_url(self, *args, **kwargs):
        url = settings.ADD_ACCOUNT_SUCCESS_URL

        return url

    def is_state_valid(self):
        # TODO: check the state in the request to prevent csrf.
        return True

    def save_account(self, provider_name, code):
        provider = registry[provider_name]
        credentials = provider.flow.step2_exchange(code=code)
        connector = provider.connector(credentials)

        profile = connector.profile.get()

        try:
            account = EmailAccount.objects.get(
                user_id=profile['user_id'],
                provider_id=provider.id
            )
            account.status = EmailAccount.RESYNC  # Account already existed, so resync.
            account.username = profile['username']  # Update the username in case it changed.
        except EmailAccount.DoesNotExist:
            account = EmailAccount.objects.create(
                user_id=profile['user_id'],
                provider_id=provider.id,
                username=profile['username']
            )

        account.raw_credentials = credentials
        account.save(update_fields=['username', 'raw_credentials', 'status', ])

        return account

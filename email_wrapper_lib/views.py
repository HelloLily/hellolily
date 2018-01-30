from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from oauth2client.client import FlowExchangeError

from email_wrapper_lib.conf import settings
from email_wrapper_lib.providers import registry
from .models import EmailAccount
from email_wrapper_lib.storage import Storage
from lily.utils.views import LoginRequiredMixin


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


class AddAccountCallbackView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # TODO: split this up in different functions, for easy overriding.
        provider_name = kwargs.get('provider_name')
        url = settings.ADD_ACCOUNT_SUCCESS_URL

        # TODO: check the state in the request to prevent csrf.

        if provider_name in registry:
            code = self.request.GET.get('code')
            provider = registry[provider_name]

            try:
                credentials = provider.flow.step2_exchange(code=code)
            except FlowExchangeError:
                messages.add_message(self.request, messages.ERROR, 'Could not get credentials for your account.')
                return url

            connector = provider.connector('me', credentials)
            profile = connector.profile.get()
            connector.execute()

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

            # Set the store so the credentials will auto refresh.
            credentials.set_store(Storage(EmailAccount, 'id', account.pk, 'credentials'))
            account.credentials = credentials

            account.save(update_fields=['username', 'credentials', 'status', ])

            manager = provider.manager_class(account)
            manager.sync()

            # TODO: call manager.sync() or something.
            # sync_account.delay(account.pk)
            messages.add_message(self.request, messages.SUCCESS, '{0} was created.'.format(account.username))

        else:
            messages.add_message(self.request, messages.ERROR, 'Invalid callback, could not process your account.')

        return url

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from oauth2client.client import FlowExchangeError

from email_wrapper_lib.providers import registry
from .models import EmailAccount
from email_wrapper_lib.storage import Storage
from lily.utils.views import LoginRequiredMixin


class AddAccountView(LoginRequiredMixin, RedirectView):
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


class AddAccountCallbackView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        provider_name = kwargs.get('provider_name')
        url = reverse('base_view')  # TODO: use settings.ADD_ACCOUNT_SUCCESS_URL or something.

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

            # TODO: username is not updated if changed in ms, we need to do so.
            account, created = EmailAccount.objects.get_or_create(
                user_id=profile['user_id'],
                provider_id=provider.id,
                defaults={
                    # Username can be changed in MS, so we only use it for account creation.
                    'username': profile['username'],
                }
            )

            # Set the store so the credentials will auto refresh.
            credentials.set_store(Storage(EmailAccount, 'id', account.pk, 'credentials'))
            account.credentials = credentials

            if not created:
                account.status = EmailAccount.RESYNC

            account.save(update_fields=['credentials', 'status', ])

            # TODO: call manager.sync() or something.
            # sync_account.delay(account.pk)
            messages.add_message(self.request, messages.SUCCESS, '{0} was created.'.format(account.username))

        else:
            messages.add_message(self.request, messages.ERROR, 'Invalid callback, could not process your account.')

        return url

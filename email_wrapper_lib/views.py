from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View, RedirectView, TemplateView
from oauth2client.client import FlowExchangeError

from email_wrapper_lib.conf import settings
from email_wrapper_lib.models import EmailMessage, EmailFolder
from email_wrapper_lib.providers import registry
from .models import EmailAccount
from lily.utils.views import LoginRequiredMixin


######################################################################################################################
# TESTVIEWS ##########################################################################################################
######################################################################################################################


class MessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'email_wrapper_lib_list.html'

    def get_context_data(self, **kwargs):
        context = super(MessagesView, self).get_context_data(**kwargs)
        context['account_list'] = EmailAccount.objects.all().order_by('id')

        account_id = kwargs.get('account_id')
        if account_id:
            context['account_id'] = account_id
            base = EmailMessage.objects.filter(account_id=account_id)
            context['folder_list'] = EmailFolder.objects.filter(account_id=account_id).order_by('account_id')
        else:
            base = EmailMessage.objects.all()
            context['folder_list'] = EmailFolder.objects.all().order_by('account_id')

        context['message_list'] = base.order_by('-received_date_time')[:200]

        folder_id = kwargs.get('folder_id')
        if folder_id:
            context['folder_id'] = folder_id
            base.filter(
                folders__in=EmailFolder.objects.filter(remote_id=folder_id)
            )

        return context


class SyncView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        account_id = kwargs.get('account_id')

        if account_id:
            account_list = [EmailAccount.objects.get(pk=account_id), ]
        else:
            account_list = EmailAccount.objects.all()

        for account in account_list:
            account.manager.sync()

        return reverse('email_v3_messagesview')


######################################################################################################################
# REGULAR VIEWS ######################################################################################################
######################################################################################################################


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
        url = reverse(settings.ADD_ACCOUNT_SUCCESS_URL)

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
                provider=provider.id
            )
            account.status = EmailAccount.RESYNC  # Account already existed, so resync.
            account.username = profile['username']  # Update the username in case it changed.
        except EmailAccount.DoesNotExist:
            account = EmailAccount.objects.create(
                user_id=profile['user_id'],
                provider=provider.id,
                username=profile['username']
            )

        account.raw_credentials = credentials
        account.save(update_fields=['username', 'raw_credentials', 'status', ])

        return account

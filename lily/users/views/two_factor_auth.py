from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django_otp.plugins.otp_static.models import StaticToken, StaticDevice
from two_factor.forms import MethodForm, TOTPDeviceForm, YubiKeyDeviceForm, BackupTokenForm
from two_factor.models import PhoneDevice
from two_factor.views import LoginView, SetupView, PhoneSetupView
from two_factor.views.utils import class_view_decorator

from lily.users.forms.two_factor_auth import (
    TwoFactorPhoneNumberForm, TwoFactorAuthenticationForm, TwoFactorAuthenticationTokenForm,
    TwoFactorDeviceValidationForm
)

FRONTEND_TWO_FACTOR_URL = '/#/preferences/user/security'


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class TwoFactorLoginView(LoginView):
    template_name = 'users/two_factor_auth/login_wizard.html'
    form_list = (
        ('auth', TwoFactorAuthenticationForm),
        ('token', TwoFactorAuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def dispatch(self, request, *args, **kwargs):
        redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')
        if (
                redirect_to.startswith(settings.STATIC_URL) or
                redirect_to.startswith(settings.MEDIA_URL) or
                redirect_to == reverse('favicon')
        ):
            redirect_to = '/'
            request.GET = request.GET.copy()
            request.GET[REDIRECT_FIELD_NAME] = redirect_to

        if request.method == 'GET':
            if request.user.is_authenticated and request.path == settings.LOGIN_URL:
                # Ensure the user-originating redirection url is safe.
                if not is_safe_url(url=redirect_to, allowed_hosts={request.get_host()}):
                    redirect_to = reverse('base_view')

                return HttpResponseRedirect(redirect_to)

        return super(TwoFactorLoginView, self).dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        device = getattr(self.get_user(), 'otp_device', None)

        if isinstance(device, StaticDevice):
            # User logged in using a static backup code, refresh it with a new one.
            device.token_set.create(token=StaticToken.random_token())

        return super(TwoFactorLoginView, self).done(form_list, **kwargs)


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class TwoFactorSetupView(SetupView):
    success_url = FRONTEND_TWO_FACTOR_URL
    qrcode_url = 'qr_code'
    template_name = 'users/two_factor_auth/setup.html'
    number_of_tokens = 10
    form_list = (
        ('method', MethodForm),
        ('generator', TOTPDeviceForm),
        ('sms', TwoFactorPhoneNumberForm),
        ('validation', TwoFactorDeviceValidationForm),
        ('yubikey', YubiKeyDeviceForm),
    )

    def done(self, form_list, **kwargs):
        device = self.request.user.staticdevice_set.get_or_create(name='backup')[0]
        device.token_set.all().delete()
        for n in range(self.number_of_tokens):
            device.token_set.create(token=StaticToken.random_token())

        messages.success(self.request, 'You have successfully setup two factor authentication!')

        return super(TwoFactorSetupView, self).done(form_list, **kwargs)


class TwoFactorPhoneSetupView(PhoneSetupView):
    template_name = 'users/two_factor_auth/phone_register.html'
    success_url = FRONTEND_TWO_FACTOR_URL
    form_list = (
        ('setup', TwoFactorPhoneNumberForm),
        ('validation', TwoFactorDeviceValidationForm),
    )

    def done(self, form_list, **kwargs):
        """
        Store the device and redirect to profile page.
        """
        device, created = PhoneDevice.objects.get_or_create(
            user=self.request.user,
            name='backup',
            method='sms',
            defaults={
                'key': self.get_key(),
            },
            **self.storage.validated_step_data.get('setup', {})
        )

        if created:
            messages.success(self.request, 'You have successfully added a backup phone number!')
        else:
            messages.info(self.request, 'You already had this phone number as a backup device.')

        return redirect(self.success_url)

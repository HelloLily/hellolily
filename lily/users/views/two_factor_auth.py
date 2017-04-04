from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django_otp.plugins.otp_static.models import StaticToken, StaticDevice
from two_factor.forms import (
    MethodForm, TOTPDeviceForm, PhoneNumberForm, YubiKeyDeviceForm, BackupTokenForm
)
from two_factor.models import PhoneDevice
from two_factor.views import LoginView, SetupView, PhoneSetupView
from two_factor.views.utils import class_view_decorator

from lily.users.forms.two_factor_auth import (
    TwoFactorPhoneNumberMethodForm, TwoFactorAuthenticationForm, TwoFactorAuthenticationTokenForm,
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
        ('sms', PhoneNumberForm),
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
        ('setup', TwoFactorPhoneNumberMethodForm),
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

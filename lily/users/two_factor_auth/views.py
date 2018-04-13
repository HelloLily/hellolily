from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django_otp.plugins.otp_static.models import StaticToken
from two_factor.forms import MethodForm, TOTPDeviceForm, YubiKeyDeviceForm
from two_factor.models import PhoneDevice
from two_factor.views import SetupView, PhoneSetupView
from two_factor.views.utils import class_view_decorator

from .forms import CustomPhoneNumberForm, CustomDeviceValidationForm


FRONTEND_TWO_FACTOR_URL = '/#/preferences/user/security'


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
        ('sms', CustomPhoneNumberForm),
        ('validation', CustomDeviceValidationForm),
        ('yubikey', YubiKeyDeviceForm),
    )

    def get(self, request, *args, **kwargs):
        if not request.user.has_usable_password():
            messages.error(
                request,
                'Cannot enable two factor auth now, please enable regular login by adding a password first.'
            )
            return redirect(self.success_url)

        return super(TwoFactorSetupView, self).get(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        device = self.request.user.staticdevice_set.get_or_create(name='backup')[0]
        device.token_set.all().delete()
        for n in range(self.number_of_tokens):
            device.token_set.create(token=StaticToken.random_token())

        messages.success(self.request, 'You have successfully set up two factor authentication!')

        return super(TwoFactorSetupView, self).done(form_list, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(TwoFactorSetupView, self).get_context_data(form, **kwargs)

        if self.steps.current == 'generator':
            context['key'] = self.request.session[self.session_key_name]

        return context


class TwoFactorPhoneSetupView(PhoneSetupView):
    template_name = 'users/two_factor_auth/phone_register.html'
    success_url = FRONTEND_TWO_FACTOR_URL
    form_list = (
        ('setup', CustomPhoneNumberForm),
        ('validation', CustomDeviceValidationForm),
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

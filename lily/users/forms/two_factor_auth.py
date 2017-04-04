from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from two_factor.forms import AuthenticationTokenForm, DeviceValidationForm
from two_factor.models import PhoneDevice
from two_factor.utils import totp_digits
from two_factor.validators import validate_international_phonenumber


class TwoFactorAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={
        'autofocus': True,
    }))


class TwoFactorAuthenticationTokenForm(AuthenticationTokenForm):
    otp_token = forms.IntegerField(label=_("Token"), min_value=1, max_value=int('9' * totp_digits()),
                                   widget=forms.NumberInput(attrs={'class': 'auth-token-input'}))


class TwoFactorDeviceValidationForm(DeviceValidationForm):
    token = forms.IntegerField(label=_("Token"), min_value=1, max_value=int('9' * totp_digits()),
                               widget=forms.NumberInput(attrs={'class': 'auth-token-input'}))


class TwoFactorPhoneNumberMethodForm(forms.ModelForm):
    number = forms.CharField(label=_("Phone Number"), validators=[validate_international_phonenumber])

    class Meta:
        model = PhoneDevice
        fields = ('number', )

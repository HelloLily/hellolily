import phonenumbers
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from phonenumbers import NumberParseException, PhoneNumberType
from two_factor.forms import AuthenticationTokenForm, DeviceValidationForm, PhoneNumberForm
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


class TwoFactorPhoneNumberForm(PhoneNumberForm):
    def clean_number(self):
        try:
            data = phonenumbers.parse(self.cleaned_data['number'], None)

            if not phonenumbers.number_type(data) == PhoneNumberType.MOBILE:
                raise forms.ValidationError('Please enter a valid mobile phone number.')

        except NumberParseException:
            raise forms.ValidationError(validate_international_phonenumber.message)

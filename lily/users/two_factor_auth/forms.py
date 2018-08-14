from django import forms
from django.utils.translation import ugettext_lazy as _
from phonenumbers import PhoneNumberType, parse, number_type, NumberParseException
from two_factor.forms import AuthenticationTokenForm, DeviceValidationForm, PhoneNumberForm
from two_factor.utils import totp_digits
from two_factor.validators import validate_international_phonenumber


class CustomAuthenticationTokenForm(AuthenticationTokenForm):
    otp_token = forms.IntegerField(
        label=_("Token"),
        min_value=1,
        max_value=int('9' * totp_digits()),
        widget=forms.NumberInput(attrs={
            'class': 'auth-token-input',
        })
    )


class CustomDeviceValidationForm(DeviceValidationForm):
    token = forms.IntegerField(
        label=_("Token"),
        min_value=1,
        max_value=int('9' * totp_digits()),
        widget=forms.NumberInput(attrs={
            'class': 'auth-token-input',
        })
    )


class CustomPhoneNumberForm(PhoneNumberForm):
    def clean_number(self):
        try:
            data = parse(self.cleaned_data['number'], None)

            if not number_type(data) == PhoneNumberType.MOBILE:
                raise forms.ValidationError('Please enter a valid mobile phone number.')

            return '+{}{}'.format(data.country_code, data.national_number)
        except NumberParseException:
            raise forms.ValidationError(validate_international_phonenumber.message)

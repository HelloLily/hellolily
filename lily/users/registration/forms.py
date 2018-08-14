import freemail
from django import forms
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from lily.messaging.email.models.models import EmailAccount
from lily.users.models import LilyUser
from lily.utils.countries import COUNTRIES


class RegistrationAuthForm(forms.Form):
    email = forms.CharField(
        label=_('Email address'),
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'placeholder': 'youremail@example.com',
                'autocomplete': 'email',
            }
        )
    )

    password = forms.CharField(
        label=_('Password'),
        strip=False,
        min_length=6,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password (at least 6 characters)',
                'class': 'hideshowpassword',
                'autocomplete': 'current-password',
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if freemail.is_disposable(email):
            raise forms.ValidationError('Please use a non-disposable email address.')

        if LilyUser.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email address already exists.')

        return email


class RegistrationVerifyEmailForm(forms.Form):
    code = forms.CharField(
        label=_('Code'),
        max_length=6,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Your six digit code',
        })
    )

    def __init__(self, code, *args, **kwargs):
        super(RegistrationVerifyEmailForm, self).__init__(*args, **kwargs)

        self.correct_code = force_text(code)

    def clean_code(self):
        code = self.cleaned_data['code']

        if not code == self.correct_code:
            raise forms.ValidationError('This code is not correct.')

        return code


class RegistrationProfileForm(forms.Form):
    first_name = forms.CharField(
        label=_('First name'),
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'placeholder': 'First name',
                'autocomplete': 'given-name additional-name',
            }
        )
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        })
    )
    company_name = forms.CharField(
        label=_('Company name'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Company name',
            'autocomplete': 'organization',
        })
    )
    country = forms.ChoiceField(
        label=_('Country'), choices=COUNTRIES, widget=forms.Select(attrs={
            'autocomplete': 'country',
        })
    )


class RegistrationEmailAccountSetupForm(forms.Form):
    pass


class RegistrationEmailAccountForm(forms.Form):
    PRIVACY_CHOICES = (
        (EmailAccount.PUBLIC, _('Group: everybody can send and read')),
        (EmailAccount.READ_ONLY, _('Personal: everybody can read, but not send')),
        (EmailAccount.METADATA, _('Sensitive: only you can see message content')),
        (EmailAccount.PRIVATE, _('Private: nothing is shared, only you have access')),
    )

    ONLY_NEW_CHOICES = (
        (False, _('Sync all messages in my inbox')),
        (True, _('Only sync messages I receive or edit starting now')),
    )

    from_name = forms.CharField(label=_('From name'), max_length=255)
    label = forms.CharField(label=_('Mailbox name'), max_length=255)
    privacy = forms.ChoiceField(label=_('Sharing'), choices=PRIVACY_CHOICES)
    only_new = forms.ChoiceField(label=_('History'), choices=ONLY_NEW_CHOICES)


class RegistrationAutofillForm(forms.Form):
    pass


class RegistrationConfirmationForm(forms.Form):
    pass

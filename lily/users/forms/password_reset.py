from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.translation import ugettext_lazy as _
from django_password_strength.widgets import PasswordStrengthInput, PasswordConfirmationInput

from lily.utils.forms.widgets import AddonTextInput


class CustomPasswordResetForm(PasswordResetForm):
    """
    This form is a subclass from the default PasswordResetForm.
    LilyUser is used for validation instead of User.
    """
    email = forms.EmailField(
        label=_('Email address'),
        max_length=255,
        widget=AddonTextInput(
            icon_attrs={
                'class': 'fa fa-user',
                'position': 'left',
                'is_button': False
            },
            attrs={
                'class': 'form-control placeholder-no-fix',
                'autocomplete': 'off',
                'placeholder': _('Email address'),
            }
        )
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    This form is a subclass from the default SetPasswordForm.
    LilyUser is used for validation instead of User.
    """
    new_password1 = forms.CharField(label=_('New password'), widget=PasswordStrengthInput())
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=PasswordConfirmationInput(confirm_with='new_password1'),
    )

from django import forms
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django_password_strength.widgets import PasswordStrengthInput, PasswordConfirmationInput

from lily.utils.forms.widgets import AddonTextInput

from .models import LilyUser


class CustomAuthenticationForm(AuthenticationForm):
    """
    This form is a subclass from the default AuthenticationForm. Necessary to set CSS classes and
    custom error_messages.
    """

    error_messages = {
        'invalid_login': _("Please enter a correct email address and password."),
        'no_cookies': _("Your web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    username = forms.EmailField(
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

    password = forms.CharField(
        label=_('Password'),
        max_length=255,
        widget=AddonTextInput(
            icon_attrs={
                'class': 'fa fa-lock',
                'position': 'left',
                'is_button': False
            },
            attrs={
                'class': 'form-control placeholder-no-fix',
                'autocomplete': 'off',
                'placeholder': _('Password'),
                'type': 'password'
            }
        )
    )

    remember_me = forms.BooleanField(label=_('Remember me'), required=False)


class CustomPasswordResetForm(PasswordResetForm):
    """
    This form is a subclass from the default PasswordResetForm.
    LilyUser is used for validation instead of User.
    """
    error_messages = {
        'unknown': _("That email address doesn't have an associated user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this email address cannot reset the password."),
        'inactive_error_message': _('You cannot request a password reset for an account that is inactive.'),
    }

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

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = LilyUser.objects.filter(email__iexact=email)

        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        else:
            for user in self.users_cache:
                if not user.is_active:
                    raise forms.ValidationError(self.error_messages['inactive_error_message'])

        return email


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


class ResendActivationForm(forms.Form):
    """
    Form that allows a user to retry sending the activation email.
    """
    error_messages = {
        'unknown': _("That email address doesn't have an associated user account. Are you sure you've registered?"),
        'active': _("You cannot request a new activation email for an account that is already active."),
    }

    email = forms.EmailField(
        label=_('Email address'),
        max_length=255,
        widget=AddonTextInput(
            icon_attrs={'class': 'fa fa-user',
                        'position': 'left',
                        'is_button': False
                        },
            attrs={'class': 'form-control placeholder-no-fix',
                   'autocomplete': 'off',
                   'placeholder': _('Email address'),
                   }
        )
    )

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data['email']
        users_cache = LilyUser.objects.filter(email__iexact=email)
        if not len(users_cache):
            raise ValidationError(code='invalid', message=self.error_messages['unknown'])
        else:
            for user in users_cache:
                if user.is_active:
                    raise ValidationError(code='invalid', message=self.error_messages['active'])
        return email


class RegistrationForm(forms.Form):
    """
    This form allows new user registration.
    """
    email = forms.EmailField(label=_('Email'), max_length=255)
    password = forms.CharField(
        label=_('Password'),
        min_length=6,
        widget=PasswordStrengthInput(),
        help_text='Password should be at least 6 characters long.',
    )
    password_repeat = forms.CharField(
        label=_('Confirm password'),
        min_length=6,
        widget=PasswordConfirmationInput(confirm_with='password'),
    )

    first_name = forms.CharField(label=_('First name'), max_length=255)
    last_name = forms.CharField(label=_('Last name'), max_length=255)

    def clean_email(self):
        if LilyUser.objects.filter(email__iexact=self.cleaned_data['email']).exists():
            raise ValidationError(code='invalid', message=_('Email address already in use.'))
        else:
            return self.cleaned_data['email']

    def clean(self):
        """
        Form validation: passwords should match and email should be unique.
        """
        cleaned_data = super(RegistrationForm, self).clean()

        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password != password_repeat:
            self._errors['password'] = self.error_class([_('The two password fields didn\'t match.')])

        return cleaned_data


class UserRegistrationForm(RegistrationForm):
    """
    Form for accepting invitations.
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-email disabled',
            'readonly': 'readonly',
        })
    )

    def clean_email(self):
        if self.cleaned_data['email'] != self.initial['email']:
            raise ValidationError(code='invalid', message=_('You can\'t change the email address of the invitation.'))
        else:
            return self.cleaned_data['email']


class InvitationForm(forms.Form):
    """
    This is the invitation form, it is used to invite new users to join an account.
    """
    first_name = forms.CharField(
        label=_('First name'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': _('First name')
        })
    )
    email = forms.EmailField(
        label=_('Email'),
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Email address')
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            LilyUser.objects.get(email__iexact=email)
        except LilyUser.DoesNotExist:
            return email
        else:
            raise ValidationError(code='invalid', message=_('This email address is already linked to a user.'))


# ------------------------------------------------------------------------------------------------
# Formsets
# ------------------------------------------------------------------------------------------------
class RequiredFirstFormFormset(BaseFormSet):
    """
    This formset requires that the first form that is submitted is filled in.
    """
    def __init__(self, *args, **kwargs):
        super(RequiredFirstFormFormset, self).__init__(*args, **kwargs)

        try:
            self.forms[0].empty_permitted = False
        except IndexError:
            print "index error bij de init van required first form formset"

    def clean(self):
        if self.total_form_count() < 1:
            raise forms.ValidationError(_("We need some data before we can proceed. Fill out at least one form."))


class RequiredFormset(BaseFormSet):
    """
    This formset requires all the forms that are submitted are filled in.
    """
    # TODO: check the extra parameter to statisfy that all initial forms are filled in.
    def __init__(self, *args, **kwargs):
        super(RequiredFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class InvitationFormset(RequiredFirstFormFormset):
    """
    This formset is sending invitations to users based on email addresses.
    """
    def clean(self):
        """Checks that no two email addresses are the same."""
        super(InvitationFormset, self).clean()

        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        emails = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            email = form.cleaned_data['email']
            if email and email in emails:
                raise ValidationError(
                    code='invalid',
                    message=_('You can\'t invite someone more than once (email addresses must be unique).')
                )
            emails.append(email)

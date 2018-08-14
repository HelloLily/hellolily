from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.utils.translation import ugettext_lazy as _
from templated_email import send_templated_mail

from lily.users.models import LilyUser


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _('Please enter a correct %(username)s and password.'),
        'inactive': _('This account is inactive.'),
    }

    username = forms.CharField(
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
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'hideshowpassword',
                'autocomplete': 'current-password',
            }
        ),
    )


class CustomPasswordResetForm(PasswordResetForm):
    """
    This form is a subclass from the default PasswordResetForm.
    LilyUser is used for validation instead of User.
    """
    email = forms.EmailField(
        label=_('Email address'),
        max_length=255,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': _('Email address'),
        })
    )

    def get_users(self, email):
        active_users = LilyUser.all_objects.filter(**{
            'email__iexact': email,
            'is_active': True,
        })
        return (u for u in active_users)

    def send_mail(
        self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None
    ):
        send_templated_mail(
            template_name=email_template_name,
            recipient_list=[
                to_email,
            ],
            context=context,
            from_email=settings.EMAIL_PERSONAL_HOST_USER,
            auth_user=settings.EMAIL_PERSONAL_HOST_USER,
            auth_password=settings.EMAIL_PERSONAL_HOST_PASSWORD
        )


class CustomSetPasswordForm(forms.Form):
    """
    This is a custom version of the Django SetPasswordForm.

    We don't want two password fields to match with each other, we want one that can display in plain text.
    LilyUser is used for validation instead of User.
    """

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)

    password = forms.CharField(
        label=_("New password"),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={
                'autofocus': True,
                'placeholder': 'Password',
                'class': 'hideshowpassword',
            }
        ),
    )

    def save(self, commit=True):
        password = self.cleaned_data["password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

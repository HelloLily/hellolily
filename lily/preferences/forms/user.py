from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_password_strength.widgets import PasswordStrengthInput
from django_password_strength.widgets import PasswordConfirmationInput

from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.forms import HelloLilyModelForm


class UserAccountForm(HelloLilyModelForm):
    old_password = forms.CharField(label=_('Current password'), widget=forms.PasswordInput())
    new_password1 = forms.CharField(label=_('New password'), widget=PasswordStrengthInput(), required=False)
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=PasswordConfirmationInput(confirm_with='new_password1'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserAccountForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = False
        self.fields['old_password'].help_text = '<a href="%s" tabindex="-1">%s</a>' % (
            reverse('password_reset'),
            unicode(_('Forgot your password?'))
        )

    def clean(self):
        cleaned_data = super(UserAccountForm, self).clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 or new_password2:
            if not new_password1 == new_password2:
                self._errors["new_password2"] = self.error_class([_('Your passwords don\'t match.')])

        return cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        logged_in_user = get_current_user()

        if not logged_in_user.check_password(old_password):
            self._errors["old_password"] = self.error_class([_('Password is incorrect.')])

        return old_password

    def save(self, commit=True):
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            logged_in_user = get_current_user()
            logged_in_user.set_password(new_password)
            logged_in_user.save()

        return super(UserAccountForm, self).save(commit)

    class Meta:
        model = LilyUser
        fieldsets = [
            (_('Change your email address'), {'fields': ['email', ], }),
            (_('Change your password'), {'fields': ['new_password1', 'new_password2', ], }),
            (_('Confirm your password'), {'fields': ['old_password', ], })
        ]

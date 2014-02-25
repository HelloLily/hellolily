from django import forms
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.forms import Form
from django.forms.formsets import BaseFormSet
from django.template import loader
from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _

from lily.users.models import CustomUser
from lily.utils.widgets import JqueryPasswordInput


class CustomAuthenticationForm(AuthenticationForm):
    """
    This form is a subclass from the default AuthenticationForm. Necessary to set CSS classes and
    custom error_messages.
    """
    error_messages = {
        'invalid_login': _("Please enter a correct e-mail address and password. "
                           "Note that both fields are case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    username = forms.CharField(label=_('Email address'), max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control placeholder-no-fix',
        'autocomplete': 'off',
        'placeholder': _('Email address'),
    }))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={
        'class': 'form-control placeholder-no-fix',
        'autocomplete': 'off',
        'placeholder': _('Password'),
    }))
    remember_me = forms.BooleanField(label=_('Remember me on this device'), required=False)


class CustomPasswordResetForm(PasswordResetForm):
    """
    This form is a subclass from the default PasswordResetForm.
    CustomUser is used for validation instead of User.
    """
    inactive_error_message = _('You cannot request a password reset for an account that is inactive.')

    email = forms.EmailField(label=_('Email address'), max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control placeholder-no-fix',
            'placeholder': _('Email address'),
    }))

    def form_valid(self, form):
        """
        Overloading super().form_valid to add a message telling an e-mail was sent.
        """

        # Send e-mail
        super(CustomPasswordResetForm, self).form_valid(form)

        # Show message
        messages.info(self.request, _('An <nobr>e-mail</nobr> with reset instructions has been sent to %s.') % form.cleaned_data.get('email'))

        return self.get_success_url()

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = CustomUser.objects.filter(
                                contact__email_addresses__email_address__iexact=email,
                                contact__email_addresses__is_primary=True,
                                is_active=True
                            )

        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        else:
            for user in self.users_cache:
                if not user.is_active:
                    raise forms.ValidationError(self.inactive_error_message)
        if any((user.password == UNUSABLE_PASSWORD)
               for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Overloading super().save to use a custom email_template_name.
        """
        email_template_name = 'email/password_reset.email'
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.primary_email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [str(user.primary_email)])


class CustomSetPasswordForm(SetPasswordForm):
    """
    This form is a subclass from the default SetPasswordForm.
    CustomUser is used for validation instead of User.
    """
    new_password1 = forms.CharField(label=_('New password'), widget=JqueryPasswordInput())
    new_password2 = forms.CharField(label=_('Confirmation'), widget=forms.PasswordInput())


class ResendActivationForm(Form):
    """
    Form that allows a user to retry sending the activation e-mail.
    """
    error_messages = {
        'unknown': _("That e-mail address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'active': _("You cannot request a new activation e-mail for an "
                    "account that is already active."),
    }

    email = forms.EmailField(label=_('E-mail address'), max_length=255)

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data['email']
        self.users_cache = CustomUser.objects.filter(
                                contact__email_addresses__email_address__iexact=email,
                                contact__email_addresses__is_primary=True
                            )
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        else:
            for user in self.users_cache:
                if user.is_active:
                    raise forms.ValidationError(self.error_messages['active'])
        return email


class RegistrationForm(Form):
    """
    This form allows new user registration.
    """
    email = forms.EmailField(label=_('E-mail'), max_length=255)
    password = forms.CharField(label=_('Password'), min_length=6,
        widget=JqueryPasswordInput())
    password_repeat = forms.CharField(label=_('Password confirmation'), min_length=6,
        widget=forms.PasswordInput())
    first_name = forms.CharField(label=_('First name'), max_length=255)
    preposition = forms.CharField(label=_('Preposition'), max_length=100, required=False)
    last_name = forms.CharField(label=_('Last name'), max_length=255)
    company = forms.CharField(label=_('Company'), max_length=255)

    def clean(self):
        """
        Form validation: passwords should match and email should be unique.
        """
        cleaned_data = super(RegistrationForm, self).clean()

        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password != password_repeat:
            self._errors['password'] = self.error_class([_('The two password fields didn\'t match.')])

        if cleaned_data.get('username'):
            try:
                CustomUser.objects.get(username=cleaned_data.get('username'))
                self._errors['username'] = self.error_class([_('Username already exists.')])
            except CustomUser.DoesNotExist:
                pass

        if cleaned_data.get('email'):
            if CustomUser.objects.filter(
                contact__email_addresses__email_address__iexact=cleaned_data.get('email')
            ).exists():
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])

        return cleaned_data


class UserRegistrationForm(RegistrationForm):
    """
    Form for accepting invitations.
    """
    email = forms.EmailField(label=_('E-mail'), max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-email disabled',
            'readonly': 'readonly',
        }
    ))
    company = forms.CharField(label=_('Company'), max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-company disabled',
            'readonly': 'readonly'
        }
    ))

    def clean(self):
        initial_email = self.initial['email']
        initial_company = self.initial['company']

        cleaned_data = super(UserRegistrationForm, self).clean()

        if cleaned_data.get('email') and cleaned_data.get('email') != initial_email:
            self._errors['email'] = self.error_class([_('You can\'t change the e-mail address of the invitation.')])

        if cleaned_data.get('company') and cleaned_data.get('company') != initial_company:
            self._errors['company'] = self.error_class([_('You can\'t change the company name of the invitation.')])

        return cleaned_data


class InvitationForm(Form):
    """
    This is the invitation form, it is used to invite new users to join an account.
    """
    first_name = forms.CharField(label=_('First name'), max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': _('First name')
        }
    ))
    email = forms.EmailField(label=_('E-mail'), max_length=255, required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Email Address')
        }
    ))

    def clean(self):
        cleaned_data = super(InvitationForm, self).clean()
        email = cleaned_data.get('email')

        if email:
            try:
                CustomUser.objects.get(contact__email_addresses__email_address__iexact=email)
                self._errors['email'] = self.error_class([_('This e-mail address is already linked to a user.')])
            except CustomUser.DoesNotExist:
                pass

        return cleaned_data


## ------------------------------------------------------------------------------------------------
## Formsets
## ------------------------------------------------------------------------------------------------
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
    This formset is sending invitations to users based on e-mail addresses.
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
            email = form.cleaned_data.get('email')
            if email and email in emails:
                raise forms.ValidationError(_("You can't invite someone more than once (e-mail addresses must be unique)."))
            emails.append(email)

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, SetPasswordForm
from django.utils.translation import ugettext as _

from lily.utils.models import EmailAddressModel
from lily.users.models import UserModel

from lily.utils.functions import autostrip   

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'mws-login-username mws-textinput required',
        'placeholder': _('Username')
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mws-login-password mws-textinput required',
        'placeholder': _('Password')
    }))
    remember_me = forms.BooleanField(label=_('Remember me on this device'), required=False)

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_('E-mail'), max_length=255, widget=forms.TextInput(attrs={
        'class': 'mws-reset-email mws-textinput required',
        'placeholder': _('E-mail address')
    }))
    
    inactive_error_message = _('You cannot request a password reset for an account that is inactive.')
    
    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = UserModel.objects.filter(
                                contact__email_addresses__email_address__iexact=email, 
                                contact__email_addresses__is_primary=True
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

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_('New password'), widget=forms.PasswordInput(attrs={
        'class': 'mws-reset-password mws-textinput required',
        'placeholder': _('New password')
    }))
    new_password2 = forms.CharField(label=_('New password confirmation'), widget=forms.PasswordInput(attrs={
        'class': 'mws-reset-password mws-textinput required',
        'placeholder': _('New password confirmation')
    }))

class ResendActivationForm(forms.Form):
    email = forms.EmailField(label=_('E-mail'), max_length=255, widget=forms.TextInput(attrs={
        'class': 'mws-reset-email mws-textinput required',
        'placeholder': _('E-mail address')
    }))
    
    error_messages = {
        'unknown': _("That e-mail address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'active': _("You cannot request a new activation e-mail for an "
                    "account that is already active."),
    }
    
    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = UserModel.objects.filter(
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

class RegistrationForm(forms.Form):
    username = forms.CharField(label=_('Username'), min_length=4, max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-username mws-textinput required',
            'placeholder': _('Username')
        })
    )
    email = forms.EmailField(label=_('E-mail'), max_length=255, 
        widget=forms.TextInput(attrs={
            'class': 'mws-register-email mws-textinput required',
            'placeholder': _('E-mail')
        }
    ))
    password = forms.CharField(label=_('Password'), min_length=6, 
        widget=forms.PasswordInput(attrs={
            'class': 'mws-register-password mws-textinput required',
            'placeholder': _('Password')
        }
    ))
    password_repeat = forms.CharField(label=_('Password confirmation'), min_length=6, 
        widget=forms.PasswordInput(attrs={
            'class': 'mws-register-password mws-textinput required',
            'placeholder': _('Password confirmation')
        }
    ))
    first_name = forms.CharField(label=_('First name'), max_length=255, 
        widget=forms.TextInput(attrs={
            'class': 'mws-register-first-name mws-textinput required',
            'placeholder': _('First name')
        }
    ))
    preposition = forms.CharField(label=_('Preposition'), max_length=100, required=False, 
        widget=forms.TextInput(attrs={
            'class': 'mws-register-preposition mws-textinput',
            'placeholder': _('Preposition')
        }
    ))
    last_name = forms.CharField(label=_('Last name'), max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-last-name mws-textinput required',
            'placeholder': _('Last name')
        }
    ))
    company = forms.CharField(label=_('Company'), max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-company mws-textinput required',
            'placeholder': _('Company')
        }
    ))
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        
        if password != password_repeat:
            self._errors['password'] = self.error_class([_('The two password fields didn\'t match.')])
        
        if cleaned_data.get('username'):
            try:
                UserModel.objects.get(username=cleaned_data.get('username'))
                self._errors['username'] = self.error_class([_('Username already exists.')])
            except UserModel.DoesNotExist:
                pass
        
        if cleaned_data.get('email'): 
            try:
                EmailAddressModel.objects.get(email_address=cleaned_data.get('email'))            
                self._errors['email'] = self.error_class([_('Email address already in use.')])
            except EmailAddressModel.DoesNotExist:
                pass
            except EmailAddressModel.MultipleObjectsReturned: 
                self._errors['email'] = self.error_class([_('Email address already in use.')])
        
        return cleaned_data

RegistrationForm = autostrip(RegistrationForm)
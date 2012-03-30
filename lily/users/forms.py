from django import forms
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _
from lily.users.models import UserModel
from lily.utils.functions import autostrip
from lily.utils.models import EmailAddressModel



class CustomAuthenticationForm(AuthenticationForm):
    """
    This form is a subclass from the default AuthenticationForm.
    We just add classes to the fields here, validation is done in the parent form.
    """
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
    """
    This form is a subclass from the default PasswordResetForm.
    Css classes are added and UserModel is used for validation instead of User.
    """
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
    """
    This form is a subclass from the default SetPasswordForm.
    Css classes are added and UserModel is used for validation instead of User.
    """
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
        email = self.cleaned_data['email']
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
    """
    This is the registration form, which is used to register a new user.
    """
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
                UserModel.objects.get(username=cleaned_data.get('username'))
                self._errors['username'] = self.error_class([_('Username already exists.')])
            except UserModel.DoesNotExist:
                pass
        
        if cleaned_data.get('email'):
            try:
                UserModel.objects.filter(
                    contact__email_addresses__email_address__iexact=cleaned_data.get('email')
                )      
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])
            except UserModel.DoesNotExist:
                pass
        
        return cleaned_data

RegistrationForm = autostrip(RegistrationForm)

class UserRegistrationForm(RegistrationForm):
    email = forms.EmailField(label=_('E-mail'), max_length=255, 
        widget=forms.TextInput(attrs={
            'class': 'mws-register-email mws-textinput required disabled',
            'placeholder': _('E-mail'),
            'readonly': 'readonly'
        }
    ))
    company = forms.CharField(label=_('Company'), max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-company mws-textinput required disabled',
            'placeholder': _('Company'),
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
    
class InvitationForm(forms.Form):
    """
    This is the invitation form, it is used to invite new users to join an account
    """
    name = forms.CharField(label=_('Name'), max_length=255, 
        widget=forms.TextInput(attrs={
            'class': 'mws-register-name mws-textinput required',
            'placeholder': _('Name')
        }
    ))
    email = forms.EmailField(label=_('E-mail'), max_length=255, required=True,
        widget=forms.TextInput(attrs={
            'class': 'mws-register-email mws-textinput required',
            'placeholder': _('E-mail')
        }
    ))
    
    def clean(self):
        cleaned_data = super(InvitationForm, self).clean()
        email = cleaned_data.get('email')
        
        if email:
            try:
                UserModel.objects.get(contact__email_addresses__email_address__iexact=email)
                self._errors['email'] = self.error_class([_('This e-mail address is already linked to a user.')])
            except UserModel.DoesNotExist:
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

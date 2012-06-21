# Django imports
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

# Lily imports
from lily.messages.email.models import EmailAccount


class CreateAccountForm(ModelForm):
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mws-login-password mws-textinput required',
        'placeholder': _('Password repeat')
    }))

    class Meta:
        model = EmailAccount
        widgets = {
            'provider': forms.Select(attrs={
                'class': 'chzn-select',
            }),
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Name'),
            }),
            'email': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Email'),
            }),
            'username': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Username'),
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Password'),
                }),
        }
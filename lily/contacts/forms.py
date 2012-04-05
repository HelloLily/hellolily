from django import forms
from django.utils.translation import ugettext as _
from lily.contacts.models import ContactModel
from lily.utils.functions import autostrip

class AddContactForm(forms.models.ModelForm):
    """
    Form to add a contact which all fields available.
    """
    
    class Meta:
        model = ContactModel
        fields = ('first_name', 'preposition', 'last_name', 'gender', 'title', 'status')
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mws-textinput required',
                'placeholder': _('First name'),
            }),
            'preposition': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Preposition'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Last name'),
            }),
            'gender': forms.Select(attrs={
            }),
            'title': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Title'),
            }),
            'status': forms.Select(attrs={
            }),
        }

AddContactForm = autostrip(AddContactForm)


class EditContactForm(forms.models.ModelForm):
    """
    Form for editing an existing contact which includes all fields available.
    """
    
    class Meta:
        model = ContactModel
        fields = ('first_name', 'preposition', 'last_name', 'gender', 'title', 'status')
                
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mws-textinput required',
                'placeholder': _('First name'),
            }),
            'preposition': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Preposition'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Last name'),
            }),
            'gender': forms.Select(attrs={
            }),
            'title': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Title'),
            }),
            'status': forms.Select(attrs={
            }),
        }
    
EditAccountForm = autostrip(EditContactForm)
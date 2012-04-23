from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.utils.functions import autostrip


class AddContactForm(ModelForm):
    """
    Form to add a contact which all fields available.
    """
    accounts = forms.ModelMultipleChoiceField(required=False,
        queryset=Account.objects.all(),
        widget=forms.SelectMultiple(attrs={ 'class': 'chzn-select' })
    )
    
    edit_accounts = forms.BooleanField(required=False, label=_('Edit these next to provide more information'),
        widget=forms.CheckboxInput())
    
    def clean(self):
        """
        Form validation: fill in at least first or last name.
        """
        cleaned_data = super(AddContactForm, self).clean()
        
        # check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])
        
        return cleaned_data
    
    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'gender', 'title', 'status', 'description')
        
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
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '5',
                'placeholder': _('Description'),
            }),
        }

AddContactForm = autostrip(AddContactForm)


class EditContactForm(ModelForm):
    """
    Form for editing an existing contact which includes all fields available.
    """
    edit_accounts = forms.BooleanField(required=False, label=_('Edit these next to provide more information'),
        widget=forms.CheckboxInput())
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        
        super(EditContactForm, self).__init__(data, files, auto_id, prefix, initial, error_class, 
                                              label_suffix, empty_permitted, instance)
    
        # Add field to select accounts where this contact works or has worked at.
        self.fields['accounts'] = forms.ModelMultipleChoiceField(required=False,
            queryset=Account.objects.all(),
            initial=Account.objects.filter(pk__in=Function.objects.filter(contact=instance).values('account_id')),
            widget=forms.SelectMultiple(attrs={ 'class': 'chzn-select' })
        )
    
    def clean(self):
        """
        Form validation: fill in at least first or last name.
        """
        cleaned_data = super(EditContactForm, self).clean()
        
        # check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])
        
        return cleaned_data
    
    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'gender', 'title', 'status', 'description')
                
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
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '5',
                'placeholder': _('Description'),
            }),
        }
    
EditContactForm = autostrip(EditContactForm)


class EditFunctionForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(EditFunctionForm, self).__init__(*args, **kwargs)
        
        # Make all fields not required
        for key, field in self.fields.iteritems():
            self.fields[key].required = False
    
    def is_valid(self):
        """
        Overloading super().is_valid to validate all functions.
        """
        is_valid = super(EditFunctionForm, self).is_valid()
        
        # Validate formset
        for form in self.formset:
            if not form.is_valid():
                is_valid = False
        
        return is_valid

class FunctionForm(ModelForm):
    """
    Form to link contacts with accounts through functions.
    """
    
    def is_valid(self):
        """
        Overloading super().is_valid to also validate all formsets.
        """
        is_valid = super(FunctionForm, self).is_valid()
        
        # Check e-mail addresses
        for form in self.email_addresses_formset:
            if not form.is_valid():
                is_valid = False
        
        # Check phone numbers
        for form in self.phone_numbers_formset:
            if not form.is_valid():
                is_valid = False
        
        return is_valid
    
    class Meta:
        exclude = ('is_deleted', 'contact', 'email_addresses', 'phone_numbers')
        widgets = {
             'title': forms.TextInput(attrs={
                 'class': 'mws-textinput',
                 'placeholder': _('Function title')
             }),
             'department': forms.TextInput(attrs={
                 'class': 'mws-textinput',
                 'placeholder': _('Department')
             })
        }
        
FunctionForm = autostrip(FunctionForm)
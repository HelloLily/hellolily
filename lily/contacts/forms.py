from django import forms
from django.forms.models import modelformset_factory
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from lily.accounts.models import AccountModel
from lily.contacts.models import ContactModel, FunctionModel
from lily.utils.forms import EmailAddressBaseForm, PhoneNumberBaseForm
from lily.utils.functions import autostrip
from lily.utils.models import EmailAddressModel, PhoneNumberModel

class AddContactForm(forms.models.ModelForm):
    """
    Form to add a contact which all fields available.
    """
    accounts = forms.ModelMultipleChoiceField(required=False,
        queryset=AccountModel.objects.all(),
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
        model = ContactModel
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
            'status': forms.Select(attrs={
            }),
        }

AddContactForm = autostrip(AddContactForm)


class EditContactForm(forms.models.ModelForm):
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
            queryset=AccountModel.objects.all(),
            initial=AccountModel.objects.filter(pk__in=FunctionModel.objects.filter(contact=instance).values('account_id')),
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
        model = ContactModel
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
            'status': forms.Select(attrs={
            }),
        }
    
EditContactForm = autostrip(EditContactForm)


class EditFunctionForm(forms.models.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(EditFunctionForm, self).__init__(*args, **kwargs)
        
        # Make all fields not required
        for key, field in self.fields.iteritems():
            self.fields[key].required = False
        

class FunctionForm(forms.models.ModelForm):
    """
    Form to link contacts with accounts through functions.
    """
    # Create basic formset
    EmailAddressFormSet = modelformset_factory(EmailAddressModel, form=EmailAddressBaseForm, can_delete=True)
    PhoneNumberFormSet = modelformset_factory(PhoneNumberModel, form=PhoneNumberBaseForm, can_delete=True)
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        super(FunctionForm, self).__init__(data, files, 'id_%s_%%s' % instance.pk, prefix, initial,
                                           error_class, label_suffix, empty_permitted, instance)
        
        # Create formsets with instance pk in the prefix
        self.email_addresses_formset = self.EmailAddressFormSet(queryset=instance.email_addresses.all(), prefix='email_addresses_%s' % instance.pk)
        self.phone_numbers_formset = self.PhoneNumberFormSet(queryset=instance.phone_numbers.all(), prefix='phone_numbers_%s' % instance.pk)
    
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
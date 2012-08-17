from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ModelForm
from django.forms.widgets import CheckboxInput, PasswordInput, DateInput, TextInput, Select, Textarea, HiddenInput
from django.utils.translation import ugettext as _

from lily.notes.models import Note
from lily.utils.models import EmailAddress, PhoneNumber, Address, COUNTRIES
from lily.utils.widgets import JqueryPasswordInput


#===================================================================================================
# Mixins
#===================================================================================================
class FieldInitFormMixin(forms.BaseForm):
    """
    FormMixin to set default widget attributes
    """
    default_widget_attrs = {
        CheckboxInput: {
            'class': {
                'append': True,
                'value': 'tabbable',
            },
        },
        DateInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable datepicker',
            },
            'placeholder': {
                'value': 'dd/mm/yyyy',
            },
        },
        JqueryPasswordInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
        },                  
        PasswordInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
        },
        Select: {
            'class': {
                'append': True,
                'value': 'chzn-select tabbable',
            },
        },
        TextInput: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
        },
        Textarea: {
            'class': {
                'append': True,
                'value': 'mws-textinput tabbable',
            },
            'rows': {
                'overwrite_defaults': True,
                'value': '4',
            },
            'cols': {
                'overwrite_defaults': True,
                'value': '55',
            },
        },
    }
    
    def __init__(self, *args, **kwargs):
        super(FieldInitFormMixin, self).__init__(*args, **kwargs)
        for name, field in self.base_fields.items():
            w = field.widget
            if issubclass(w.__class__, HiddenInput):
                continue # ignore
            
            # set placeholder if not already and field has an initial value or label
            if not 'placeholder' in w.attrs:
                if isinstance(w, TextInput) and field.initial is not None:
                    w.attrs['placeholder'] = field.initial
                elif field.label is not None:
                    if w.__class__ in [JqueryPasswordInput, PasswordInput, TextInput, Textarea]:
                        w.attrs['placeholder'] = field.label
            
            if w.__class__ is Textarea:
                # Text for click-show plugin
                if w.attrs.get('click_show_text', False):
                    w.click_show_text = w.attrs['click_show_text']
                else:
                    w.click_show_text = _('Add')  
            
            # append certain default attributes
            attrs = self.default_widget_attrs.get(w.__class__, [])
            for attr in attrs:
                if attrs[attr].get('append', False):
                    w.attrs[attr] = (w.attrs.get(attr, '') + ' ' + attrs[attr]['value']).strip()
                elif attrs[attr].get('overwrite_defaults', False):
                    w.attrs[attr] = attrs[attr]['value']
                else:
                    w.attrs[attr] = w.attrs.get(attr, attrs[attr]['value'])
            
            # add class for required fields
            if field.required:
                w.attrs['class'] = (w.attrs.get('class', '') + ' required').strip()
                
        super(FieldInitFormMixin, self).__init__(*args, **kwargs)


#===================================================================================================
# Forms
#===================================================================================================
class EmailAddressBaseForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding an e-mail address, only including the is_primary and the e-mail fields.
    """
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        
        super(EmailAddressBaseForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = EmailAddress
        fields = ('email_address', 'is_primary')
        exclude = ('status')
        widgets = {
            'email_address': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('E-mail address'),
            }),
        }

 
class PhoneNumberBaseForm(ModelForm):
    """
    Form for adding a phone number, only including the number and type/other type fields.
    """
    type = forms.ChoiceField(choices=PhoneNumber.PHONE_TYPE_CHOICES, initial='work',
        widget=forms.Select(attrs={
            'class': 'other chzn-select-no-search tabbable'
        }
    ))

    # Make raw_input not required to prevent the form from demanding input when only type
    # has been changed.
    raw_input = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'mws-textinput tabbable',
        'placeholder': _('Phone number'),
    }));

    class Meta:
        model = PhoneNumber
        fields = ('raw_input', 'type', 'other_type')
        exclude = ('status')
        widgets = {
            'other_type': forms.TextInput(attrs={
                'class': 'mws-textinput other hidden tabbable',
            }),
            'type': forms.Select(attrs={
                'class': 'tabbable'
            })
        }


class AddressBaseForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding an address which includes all fields available.
    """
    type = forms.ChoiceField(choices=Address.ADDRESS_TYPE_CHOICES, initial='visiting',
        widget=forms.Select(attrs={
            'class': 'chzn-select-no-search',
        })
    )
    country = forms.ChoiceField(choices=COUNTRIES, required=False, widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(AddressBaseForm, self).__init__(*args, **kwargs)
        
        if hasattr(self, 'exclude_address_types'):
            choices = self.fields['type'].choices
            for i in reversed(range(len(choices))):
                if choices[i][0] in self.exclude_address_types:
                    del choices[i]
            self.fields['type'].choices = choices
            
    class Meta:
        model = Address
        fields = ('street', 'street_number', 'complement', 'postal_code', 'city', 'state_province', 'country', 'type')


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ('author', 'object_id', 'content_type')
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'tabbable',
                'placeholder': _('Write your note here'),
            })
        }
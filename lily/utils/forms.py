from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.utils.functions import autostrip
from lily.utils.models import EmailAddress, PhoneNumber, Address, COUNTRIES
from lily.notes.models import Note


class EmailAddressBaseForm(ModelForm):
    """
    Form for adding an e-mail address, only including the is_primary and the e-mail fields.
    """
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


class AddressBaseForm(ModelForm):
    """
    Form for adding an address which includes all fields available.
    """
    type = forms.ChoiceField(choices=Address.ADDRESS_TYPE_CHOICES, initial='visiting',
        widget=forms.Select(attrs={
            'class': 'mws-textinput chzn-select-no-search tabbable',
        })
    )
    country = forms.ChoiceField(choices=COUNTRIES, required=False, widget=forms.Select(attrs={
        'class': 'mws-textinput chzn-select tabbable',
    }))

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
        widgets = {
            'street_number': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Number'),
            }),
            'complement': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Complement'),
            }),
            'street': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Street'),
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Postal code'),
            }),
            'city': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('City'),
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('State/province'),
            }),
        }


class AccountAddressForm(AddressBaseForm):
    exclude_address_types = ['home']


class ContactAddressForm(AddressBaseForm):
    exclude_address_types = ['visiting']


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


# Enable autostrip input on these forms
EmailAddressBaseForm = autostrip(EmailAddressBaseForm)
PhoneNumberBaseForm = autostrip(PhoneNumberBaseForm)
AddressBaseForm = autostrip(AddressBaseForm)
AccountAddressForm = autostrip(AccountAddressForm)
ContactAddressForm = autostrip(ContactAddressForm)
NoteForm = autostrip(NoteForm)
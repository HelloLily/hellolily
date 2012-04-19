from django import forms
from django.utils.translation import ugettext as _
from lily.utils.functions import autostrip
from lily.utils.models import EmailAddressModel, PhoneNumberModel, AddressModel, NoteModel


class EmailAddressBaseForm(forms.ModelForm):
    """
    Form for adding an e-mail address, only including the is_primary and the e-mail fields.
    """
    class Meta:
        model = EmailAddressModel
        exclude = ('status')
        widgets = {
            'email_address': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('E-mail address'),
            }),
        }

EmailAddressBaseForm = autostrip(EmailAddressBaseForm)


class PhoneNumberBaseForm(forms.ModelForm):
    """
    Form for adding a phone number, only including the number and type/other type fields.
    """
    type = forms.ChoiceField(choices=PhoneNumberModel.PHONE_TYPE_CHOICES, initial='work', 
        widget=forms.Select(attrs={
            'class': 'other'
        }
    ))
    
    # Make raw_input not required to prevent the form from demanding input when only type
    # has been changed.
    raw_input = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'mws-textinput',
        'placeholder': _('Phone number'),
    }));

    class Meta:
        model = PhoneNumberModel
        fields = ('raw_input', 'type', 'other_type')
        exclude = ('status')
        widgets = {
            'raw_input': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Phone number'),
            }),
            'other_type': forms.TextInput(attrs={
                'class': 'mws-textinput other hidden',
            }),
        }

PhoneNumberBaseForm = autostrip(PhoneNumberBaseForm)


class AddressBaseForm(forms.ModelForm):
    """
    Form for adding an address which includes all fields available.
    """
    type = forms.ChoiceField(choices=AddressModel.ADDRESS_TYPE_CHOICES, initial='visiting',
        widget=forms.Select()
    )
    
    class Meta:
        model = AddressModel
        fields = ('street', 'street_number', 'complement', 'postal_code', 'city', 'state_province', 'country', 'type')
        widgets = {
            'street_number': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Street number'),
            }),
            'complement': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Complement'),
            }),
            'street': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Street'),
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Postal code'),
            }),
            'city': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('City'),
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('State/province'),
            }),
            'country': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Country'),
            }),
        }

AddressBaseForm = autostrip(AddressBaseForm)

class NoteForm(forms.ModelForm):
    class Meta:
        model = NoteModel
        exclude = ('author', )
        widgets = {
            'note': forms.Textarea(attrs={
                'placeholder': _('Write your note here'),
            })
        }
from django import forms
from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _

from ..models.models import EmailAddress, PhoneNumber, Address, PHONE_TYPE_CHOICES
from lily.utils.countries import COUNTRIES


class EmailAddressBaseForm(ModelForm):
    """
    Form for adding an email address, only including the status and the email fields.
    """
    class Meta:
        model = EmailAddress
        fields = ('email_address', 'status',)
        widgets = {
            'email_address': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
            }),
        }


class PhoneNumberBaseForm(ModelForm):
    """
    Form for adding a phone number, only including the number and type/other type fields.
    """
    type = forms.ChoiceField(choices=PHONE_TYPE_CHOICES, initial='work', required=False)

    # Make number not required to prevent the form from demanding input when only type
    # has been changed.
    number = forms.CharField(label=_('Phone number'), required=False)

    def __init__(self, *args, **kwargs):
        super(PhoneNumberBaseForm, self).__init__(*args, **kwargs)

        self.fields['number'].label = _('Phone number')

    class Meta:
        model = PhoneNumber
        fields = ('number', 'type', 'other_type', )
        widgets = {
            'other_type': forms.TextInput(attrs={
                'class': 'other hidden',
            }),
        }


class AddressBaseForm(ModelForm):
    """
    Form for adding an address which includes all fields available.
    """
    type = forms.ChoiceField(
        choices=Address.ADDRESS_TYPE_CHOICES,
        initial='visiting',
        widget=forms.Select(attrs={
            'class': 'chzn-select-no-search',
        })
    )
    country = forms.ChoiceField(choices=COUNTRIES, required=False)

    def __init__(self, *args, **kwargs):
        kwargs.update(getattr(self, 'extra_form_kwargs', {}))

        super(AddressBaseForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'exclude_address_types'):
            choices = self.fields['type'].choices
            for i in reversed(range(len(choices))):
                if choices[i][0] in self.exclude_address_types:
                    del choices[i]
            self.fields['type'].choices = choices

    class Meta:
        model = Address
        fields = (
            'address',
            'postal_code',
            'city',
            'country',
            'type'
        )


class SugarCsvImportForm(Form):
    """
    Form in which a csv file can be uploaded from which
    accounts or contacts can be imported for the logged in tenant.
    """
    csvfile = forms.FileField(label=_('CSV'))
    model = forms.ChoiceField(label=_('Import rows as'), choices=(('contact', _('Contacts')),
                                                                  ('account', _('Accounts')),
                                                                  ('function', _('Functions'))))
    sugar_import = forms.ChoiceField(label=_('From source:'), choices=((1, _('Sugar')), (0, _('Other'))))

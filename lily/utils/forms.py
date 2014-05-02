from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.messaging.email.widgets import EmailAttachmentWidget
from lily.messaging.email.models import EmailAttachment
from form_utils.forms import BetterForm, BetterModelForm
from lily.utils.models import EmailAddress, PhoneNumber, Address, COUNTRIES


class HelloLilyForm(BetterForm):
    '''
    Inherit from BetterForm django-form-utils.
    We can add more custom form features here later.
    '''
    pass


class HelloLilyModelForm(BetterModelForm):
    '''
    Inherit from BetterModelForm django-form-utils.
    We can add more custom form features here later.
    '''
    pass


# Forms
class EmailAddressBaseForm(HelloLilyModelForm):
    """
    Form for adding an e-mail address, only including the is_primary and the e-mail fields.
    """
    def __init__(self, *args, **kwargs):
        super(EmailAddressBaseForm, self).__init__(*args, **kwargs)


    class Meta:
        model = EmailAddress
        fields = ('email_address',)
        exclude = ('status', 'is_primary',)
        widgets = {
            'email_address': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
            }),
        }


class PhoneNumberBaseForm(HelloLilyModelForm):
    """
    Form for adding a phone number, only including the number and type/other type fields.
    """
    type = forms.ChoiceField(choices=PhoneNumber.PHONE_TYPE_CHOICES, initial='work', required=False)

    # Make raw_input not required to prevent the form from demanding input when only type
    # has been changed.
    raw_input = forms.CharField(label=_('Phone number'), required=False)

    def __init__(self, *args, **kwargs):
        super(PhoneNumberBaseForm, self).__init__(*args, **kwargs)

        self.fields['raw_input'].label = _('Phone Number')

    class Meta:
        model = PhoneNumber
        fields = ('raw_input', 'type', 'other_type')
        exclude = ('status')
        widgets = {
            'other_type': forms.TextInput(attrs={
                'class': 'other hidden',
            }),
        }


class AddressBaseForm(HelloLilyModelForm):
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

        self.fields['street'].label = _('Address')

    class Meta:
        model = Address
        fields = ('street', 'street_number', 'complement', 'postal_code', 'city', 'country', 'type')
        exclude = ('state_provice',)


class AttachmentBaseForm(HelloLilyModelForm):
    """
    Form for uploading files.
    """
    class Meta:
        models = EmailAttachment
        fields = ('attachment',)
        exclude = ('message', 'size', 'inline', 'tenant')
        widgets = {
            'attachment': EmailAttachmentWidget(),
        }

from crispy_forms.layout import Layout, HTML
from django import forms
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.messaging.email.widgets import EmailAttachmentWidget
from lily.messaging.email.models import EmailAttachment
from lily.utils.formhelpers import LilyFormHelper
from lily.utils.layout import MultiField, Anchor, ColumnedRow, Column
from lily.utils.models import EmailAddress, PhoneNumber, Address, COUNTRIES


# Forms
class EmailAddressBaseForm(ModelForm):
    """
    Form for adding an e-mail address, only including the is_primary and the e-mail fields.
    """
    def __init__(self, *args, **kwargs):
        super(EmailAddressBaseForm, self).__init__(*args, **kwargs)

        self.fields['email_address'].label = ''
        self.fields['is_primary'].label = ''

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
    type = forms.ChoiceField(choices=PhoneNumber.PHONE_TYPE_CHOICES, initial='work', required=False)

    # Make raw_input not required to prevent the form from demanding input when only type
    # has been changed.
    raw_input = forms.CharField(label=_('Phone number'), required=False)

    def __init__(self, *args, **kwargs):
        super(PhoneNumberBaseForm, self).__init__(*args, **kwargs)

        self.fields['raw_input'].label = ''
        self.fields['type'].label = ''
        self.fields['other_type'].label = ''

    class Meta:
        model = PhoneNumber
        fields = ('raw_input', 'type', 'other_type')
        exclude = ('status')
        widgets = {
            'other_type': forms.TextInput(attrs={
                'class': 'other hidden',
            }),
        }


class AddressBaseForm(ModelForm):
    """
    Form for adding an address which includes all fields available.
    """
    type = forms.ChoiceField(choices=Address.ADDRESS_TYPE_CHOICES, initial='visiting',
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

        self.fields['street'].label = ''
        self.fields['street_number'].label = ''
        self.fields['complement'].label = ''
        self.fields['postal_code'].label = ''
        self.fields['city'].label = ''
        self.fields['country'].label = ''
        self.fields['type'].label = ''

    class Meta:
        model = Address
        fields = ('street', 'street_number', 'complement', 'postal_code', 'city', 'country', 'type')
        exclude = ('state_provice',)

class AttachmentBaseForm(ModelForm):
    """
    Form for uploading files.
    """
    def __init__(self, *args, **kwargs):
        super(AttachmentBaseForm, self).__init__(*args, **kwargs)

        anchor_url = 'javascript:void(0)'
        anchor_css_class = 'i-16 i-trash-1 blue {{ formset.prefix }}-delete-row'
        if self.instance.pk:
            anchor_url = reverse('email_attachment_removal', kwargs={'pk': self.instance.message_id, 'attachment_pk': self.instance.pk})
            anchor_css_class += ' dont'

        self.helper = LilyFormHelper(self)
        self.helper.form_tag = False
        self.helper.add_layout(Layout(
            MultiField(
                None,
                None,
                ColumnedRow(
                    Column('attachment', size=3, first=True, css_class='email-attachment-widget'),
                    Column(
                        Anchor(href=anchor_url, css_class=anchor_css_class),
                        size=1,
                        css_class='formset-delete'
                    ),
                )
            )
        ))

        self.fields['attachment'].label = ''

    class Meta:
        models = EmailAttachment
        fields = ('attachment',)
        exclude = ('message', 'size', 'inline', 'tenant')
        widgets = {
            'attachment': EmailAttachmentWidget(),
        }

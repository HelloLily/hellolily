from django import forms
from django.utils.translation import ugettext as _

from lily.accounts.models import Account, Website
from lily.tags.forms import TagsFormMixin
from lily.utils.forms import HelloLilyModelForm
from lily.utils.widgets import DataProviderInput, ShowHideWidget


class AddAccountQuickbuttonForm(HelloLilyModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(label=_('Website'), max_length=255, initial='http://', required=False, widget=DataProviderInput())
    name = forms.CharField(label=_('Company name'), max_length=255)
    primary_email = forms.EmailField(label=_('E-mail address'), max_length=255)
    phone_number = forms.CharField(label=_('Phone number'), max_length=40, required=False)

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_account_quickbutton_%s',
        })

        super(AddAccountQuickbuttonForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddAccountQuickbuttonForm, self).clean()

        # Prevent multiple accounts with the same company name
        if cleaned_data.get('name'):
            if Account.objects.filter(name=cleaned_data.get('name')).exists():
                self._errors['name'] = self.error_class([_('Company name already in use.')])

        # Prevent multiple accounts with the same e-mail adress when adding
        if cleaned_data.get('primary_email'):
            if Account.objects.filter(email_addresses__email_address__iexact=cleaned_data.get('primary_email')).exists():
                self._errors['primary_email'] = self.error_class([_('E-mail address already in use.')])

        # Prevent multiple accounts with the same primary website when adding
        if cleaned_data.get('website'):
            if Website.objects.filter(website=cleaned_data.get('website'), is_primary=True).exists():
                self._errors['website'] = self.error_class([_('Website already in use.')])

        return cleaned_data

    class Meta:
        model = Account
        fields = ('website', 'name', 'description', 'primary_email', 'phone_number', 'legalentity', 'taxnumber', 'bankaccountnumber',
                  'cocnumber', 'iban', 'bic')

        widgets = {
            'description': ShowHideWidget(forms.Textarea({
                'rows': 3,
            })),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),
        }


class CreateUpdateAccountForm(TagsFormMixin):
    """
    Form for creating or updating an account.
    """
    primary_website = forms.URLField(max_length=255, label=_('Primary website'), initial='http://', required=False, widget=DataProviderInput())

    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to set the initial value for the primary website if possible
        """
        super(CreateUpdateAccountForm, self).__init__(*args, **kwargs)

        # Provide initial data for primary website
        try:
            self.fields['primary_website'].initial = Website.objects.filter(account=self.instance, is_primary=True)[0].website
        except:
            pass

    class Meta:
        model = Account
        fields = ('primary_website', 'name', 'description', 'legalentity', 'taxnumber', 'bankaccountnumber', 'cocnumber', 'iban', 'bic')  # TODO: status field
        exclude = ('is_deleted', 'tenant', 'tags')

        widgets = {
            'description': ShowHideWidget(forms.Textarea({
                'rows': 3
            })),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),
        }


class WebsiteBaseForm(HelloLilyModelForm):
    """
    Base form for adding multiple websites to an account.
    """
    website = forms.URLField(max_length=255, initial='http://', required=False)

    class Meta:
        model = Website
        fields = ('website',)
        exclude = ('account', )

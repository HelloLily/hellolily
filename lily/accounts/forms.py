import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from lily.accounts.models import Account, Website
from lily.tags.forms import TagsFormMixin
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.fields import FormSetField, TagsField
from lily.utils.forms.formsets import BaseFKFormSet
from lily.utils.forms.widgets import ShowHideWidget, AddonTextInput
from lily.utils.forms.mixins import FormSetFormMixin
from lily.utils.models import EmailAddress, Address


class AddAccountQuickbuttonForm(HelloLilyModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(
        label=_('Website'),
        max_length=255,
        initial='http://',
        required=False,
        widget=AddonTextInput(
            icon_attrs={'class': 'icon-magic'},
            button_attrs={'class': 'btn default dataprovider'},
            div_attrs={'class': 'input-group dataprovider'}
        )
    )
    name = forms.CharField(label=_('Company name'), max_length=255)
    emails = TagsField(label=_('E-mail addresses'), required=False)
    phone_number = forms.CharField(label=_('Phone number'), max_length=40, required=False)

    # Hidden field to hold JSON address data
    addresses = forms.CharField(max_length=1024, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_account_quickbutton_%s',
        })

        super(AddAccountQuickbuttonForm, self).__init__(*args, **kwargs)

    def clean_addresses(self):
        """
        Clean JSON Address field and create python array with address dicts.
        """
        try:
            json_addresses = json.loads(self.cleaned_data['addresses'])
        except ValueError:
            pass
        else:
            # Check addresses
            address_fields = [
                'street',
                'street_number',
                'complement',
                'city',
                'country',
                'postal_code'
            ]
            parsed_addresses = []
            for address in json_addresses:
                # For each address, only add fields that match Address fields
                address_data = {}
                for field, value in address.iteritems():
                    if field in address_fields:
                        address_data[field] = value
                if address_data:
                    parsed_addresses.append(address_data)
            return parsed_addresses

    def clean_name(self):
        """
        Prevent multiple accounts with the same company name
        """
        name = self.cleaned_data['name']
        if Account.objects.filter(name=name, is_deleted=False).exists():
                raise ValidationError(
                    _('Company name already in use.'),
                    code='invalid',
                )
        else:
            return name

    def clean_emails(self):
        """
        Prevent multiple accounts with the same e-mail adress when adding
        """
        for email in self.cleaned_data['emails']:
            validate_email(email)
            if Account.objects.filter(email_addresses__email_address__iexact=email, is_deleted=False).exists():
                raise ValidationError(
                    _('E-mail address already in use.'),
                    code='invalid',
                )

        return self.cleaned_data['emails']

    def clean_website(self):
        """
        Prevent multiple accounts with the same primary website when adding
        """
        website = self.cleaned_data['website']
        if Website.objects.filter(website=website, is_primary=True, account__is_deleted=False).exists():
            raise ValidationError(
                _('Website already in use.'),
                code='invalid',
            )
        else:
            return website

    def save(self, commit=True):
        """
        Save Many2Many email addresses to instance.
        """
        instance = super(AddAccountQuickbuttonForm, self).save(commit=commit)

        if commit:
            # Save email addresses
            first = True
            for email in self.cleaned_data['emails']:
                email_address = EmailAddress.objects.create(
                    email_address=email,
                    is_primary=first,
                    tenant=instance.tenant
                )
                instance.email_addresses.add(email_address)
                first = False

            # Save addresses
            for address in self.cleaned_data['addresses']:
                instance.addresses.add(Address.objects.create(**address))

        return instance

    class Meta:
        model = Account
        fields = (
            'website',
            'name',
            'description',
            'emails',
            'phone_number',
            'legalentity',
            'taxnumber',
            'bankaccountnumber',
            'cocnumber',
            'iban',
            'bic',
        )

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


class WebsiteBaseForm(HelloLilyModelForm):
    """
    Base form for adding multiple websites to an account.
    """
    website = forms.URLField(max_length=255, initial='http://', required=False, label=_('Extra website(s)'))

    class Meta:
        model = Website
        fields = ('website',)


class CreateUpdateAccountForm(FormSetFormMixin, TagsFormMixin):
    """
    Form for creating or updating an account.
    """
    primary_website = forms.URLField(max_length=255, label=_('Primary website'), initial='http://', required=False,
                                     widget=AddonTextInput(icon_attrs={'class': 'icon-magic'},
                                                           button_attrs={'class': 'btn default dataprovider'},
                                                           div_attrs={'class': 'input-group dataprovider'}))
    extra_websites = FormSetField(
        queryset=Website.objects,
        formset_class=modelformset_factory(
            Website,
            form=WebsiteBaseForm,
            formset=BaseFKFormSet,
            can_delete=True,
            extra=0
        ),
        template='accounts/formset_website.html',
        related_name='account',
    )

    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to set the initial value for the primary website if possible.
        Also set initial data for the websites field and set form_attrs for addresses formsetfield.
        """
        super(CreateUpdateAccountForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['extra_websites'].initial = self.instance.websites.filter(is_primary=False)

        # Provide initial data for primary website
        try:
            self.fields['primary_website'].initial = Website.objects.filter(account=self.instance, is_primary=True)[0].website
        except IndexError:
            pass

    class Meta:
        model = Account
        fields = ('primary_website', 'name', 'description', 'legalentity', 'taxnumber', 'bankaccountnumber', 'cocnumber',
                  'iban', 'bic', 'email_addresses', 'phone_numbers', 'addresses', 'extra_websites', )  # TODO: status field

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

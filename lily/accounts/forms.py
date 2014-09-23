from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from lily.accounts.models import Account, Website
from lily.tags.forms import TagsFormMixin
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.fields import FormSetField
from lily.utils.forms.formsets import BaseFKFormSet
from lily.utils.forms.widgets import ShowHideWidget, AddonTextInput
from lily.utils.forms.mixins import FormSetFormMixin


class AddAccountQuickbuttonForm(HelloLilyModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(label=_('Website'), max_length=255, initial='http://', required=False,
                             widget=AddonTextInput(icon_attrs={'class': 'icon-magic'},
                                                   button_attrs={'class': 'btn default dataprovider'},
                                                   div_attrs={'class': 'input-group dataprovider'}))
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

    def clean_name(self):
        """
        Prevent multiple accounts with the same company name
        """
        name = self.cleaned_data['name']
        if Account.objects.filter(name=name).exists():
                raise ValidationError(
                    _('Company name already in use.'),
                    code='invalid',
                )
        else:
            return name

    def clean_primary_email(self):
        """
        Prevent multiple accounts with the same e-mail adress when adding
        """
        primary_email = self.cleaned_data['primary_email']
        if Account.objects.filter(email_addresses__email_address__iexact=primary_email).exists():
            raise ValidationError(
                _('E-mail address already in use.'),
                code='invalid',
            )
        else:
            return primary_email

    def clean_website(self):
        """
        Prevent multiple accounts with the same primary website when adding
        """
        website = self.cleaned_data['website']
        if Website.objects.filter(website=website, is_primary=True).exists():
            raise ValidationError(
                _('Website already in use.'),
                code='invalid',
            )
        else:
            return website

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


class WebsiteBaseForm(HelloLilyModelForm):
    """
    Base form for adding multiple websites to an account.
    """
    website = forms.URLField(max_length=255, initial='http://', required=False, label=_('Extra website(s)'))

    class Meta:
        model = Website
        fields = ('website',)
        exclude = ('account', )


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
        formset_class=modelformset_factory(Website, form=WebsiteBaseForm, formset=BaseFKFormSet, can_delete=True, extra=0),
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

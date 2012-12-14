from crispy_forms.layout import Hidden, Layout
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account, Website
from lily.tags.forms import TagsFormMixin
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper, LilyFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Anchor, Column, Row, Button


class AddAccountQuickbuttonForm(ModelForm, FieldInitFormMixin):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(label=_('Website'), max_length=30, initial='http://', required=False)
    name = forms.CharField(label=_('Company name'), max_length=255)
    email = forms.EmailField(label=_('E-mail address'), max_length=255)
    phone = forms.CharField(label=_('Phone number'), max_length=40, required=False)

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_account_quickbutton_%s',
        })

        super(AddAccountQuickbuttonForm, self).__init__(*args, **kwargs)

        # Customize form layout
        self.helper = LilyFormHelper(self)
        self.helper.layout = Layout()
        self.helper.layout.insert(0, Hidden('submit_button', 'add', css_id='add-account-submit'))
        self.helper.add_columns(
            Column('website', size=7, first=True),
            Column(Button('enrich', _('Enrich'), css_id='enrich-account-button'), size=1),
        )
        self.helper.add_columns(
            Column('name', size=4, first=True),
            Column(Anchor('#', _('Edit existing account'), css_class='existing-account-link hidden'), size=4),
        )
        self.helper.add_large_fields('email', 'phone')

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
        if cleaned_data.get('email'):
            if Account.objects.filter(email_addresses__email_address__iexact=cleaned_data.get('email')).exists():
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])

        # Prevent multiple accounts with the same primary website when adding
        if cleaned_data.get('website'):
            if Website.objects.filter(website=cleaned_data.get('website'), is_primary=True).exists():
                self._errors['website'] = self.error_class([_('Website already in use.')])

        return cleaned_data

    class Meta:
        model = Account
        fields = ('website', 'name', 'email', 'phone')


class CreateUpdateAccountForm(TagsFormMixin, ModelForm, FieldInitFormMixin):
    """
    Form for creating or updating an account.
    """
    primary_website = forms.URLField(label=_('Primary website'), initial='http://', required=False)

    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to set the initial value for the primary website if possible
        and add a form helper.
        """
        super(CreateUpdateAccountForm, self).__init__(*args, **kwargs)

        # Customize form layout
        self.helper = DeleteBackAddSaveFormHelper(form=self)
        self.helper.replace('primary_website',
            self.helper.create_columns(
                Column('primary_website', size=4, first=True),
                Column(Button('enrich', _('Enrich'), css_id='enrich-account-button'), size=2),
            )
        )
        self.helper.replace('name',
            self.helper.create_columns(
                Column('name', size=4, first=True),
                Column(Anchor('#', _('Edit existing account'), css_class='existing-account-link hidden'), size=2),
            )
        )
        self.helper.wrap_by_names(Row, 'description', 'tags')

        # Provide initial data for primary website
        try:
            self.fields['primary_website'].initial = Website.objects.filter(account=self.instance, is_primary=True)[0].website
        except Exception:
            pass

    class Meta:
        model = Account
        fields = ('primary_website', 'name', 'description' , 'legalentity', 'taxnumber', 'bankaccountnumber', 'cocnumber', 'iban', 'bic') # TODO: status field
        exclude = ('is_deleted', 'tenant', 'tags')

        widgets = {
            'description': forms.Textarea({
                'click_show_text': _('Add description')
            }),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),
        }


class WebsiteBaseForm(ModelForm, FieldInitFormMixin):
    """
    Base form for adding multiple websites to an account.
    """
    website = forms.URLField(max_length=30, initial='http://', required=False)

    def __init__(self, *args, **kwargs):
        super(WebsiteBaseForm, self).__init__(*args, **kwargs)
        self.helper = LilyFormHelper(self)
        self.helper.form_tag = False
        self.helper.replace('website', self.helper.create_columns(
            Column('website', size=4, first=True),
            Column(
                Anchor(href='javascript:void(0)', css_class='i-16 i-trash-1 blue {{ formset.prefix }}-delete-row'),
                size=1,
                css_class='formset-delete'
            ),
            label=None,
            inline=True,
        ))

    class Meta:
        model = Website
        fields = ('website',)
        exclude = ('account')

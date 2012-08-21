from crispy_forms.layout import Button
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account, Website
from lily.tags.forms import TagsFormMixin
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Anchor, Column, Row, InlineRow, ColumnedRow, MultiField


class AddAccountQuickbuttonForm(ModelForm, FieldInitFormMixin):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(max_length=30, initial='http://', required=False)    
    name = forms.CharField(max_length=255, label=_('Company name'))
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
    
    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddAccountQuickbuttonForm, self).clean()

        # Prevent multiple accounts with the same company name
        if cleaned_data.get('name'):
            try:
                Account.objects.get(name=cleaned_data.get('name'))
                self._errors['name'] = self.error_class([_('Company name already in use.')])
            except Account.DoesNotExist:
                pass
        
        # Prevent multiple accounts with the same e-mail adress when adding
        if cleaned_data.get('email'):
            if Account.objects.filter(email_addresses__email_address__iexact=cleaned_data.get('email')).exists():
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])
        
        # Prevent multiple accounts with the same primary website when adding
        if cleaned_data.get('website'):
            try:
                Website.objects.get(website=cleaned_data.get('website'), is_primary=True)
                self._errors['website'] = self.error_class([_('Website already in use.')])
            except Website.DoesNotExist:
                pass 

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
        self.helper.replace('primary_website', MultiField(
            self.fields['primary_website'].label,
            InlineRow(
                ColumnedRow(
                    Column('primary_website', size=4, first=True),
                    Column(Button('enrich', _('Enrich'), css_id='enrich-account-button'), size=2)
                ),
            ),
        ))
        self.helper.replace('name', MultiField(
            self.fields['name'].label,
            InlineRow(
                ColumnedRow(
                    Column('name', size=4, first=True),
                    Column(Anchor('#', _('Edit existing account'), css_class='existing-account-link hidden'), size=2),
                ),
            ),
        ))
        self.helper.exclude_by_widgets([forms.HiddenInput]).wrap(Row)
        
        # Prevent rendering labels twice
        self.fields['name'].label = ''
        self.fields['primary_website'].label = ''
        
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
    website = forms.URLField(max_length=30, initial='http://')

    class Meta:
        model = Website
        exclude = ('account')
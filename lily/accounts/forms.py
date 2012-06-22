from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _

from lily.accounts.models import Account, Website
from lily.tags.forms import TagsFormMixin


class AddAccountMinimalForm(ModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(max_length=30, initial='http://', required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': 'http://'
    }))
    
    name = forms.CharField(max_length=255, label=_('Company name'), widget=forms.TextInput(attrs={
        'class': 'mws-textinput required',
        'placeholder': _('Company name')
    }))

    email = forms.EmailField(label=_('E-mail'), max_length=255, widget=forms.TextInput(attrs={
        'class': 'mws-textinput required',
        'placeholder': _('E-mail address')
    }))

    phone = forms.CharField(max_length=40, required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('Phone number')
    }))

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with 
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_account_quickbutton_%s',
        })
        
        super(AddAccountMinimalForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddAccountMinimalForm, self).clean()

        # Prevent multiple accounts with the same company name
        if cleaned_data.get('name'):
            try:
                Account.objects.get(name=cleaned_data.get('name'))
                self._errors['name'] = self.error_class([_('Company name already in use.')])
            except Account.DoesNotExist:
                pass
        
        # Prevent multiple accounts with the same e-mailadress when adding
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
        fields = ('name', 'email')


class AddAccountForm(TagsFormMixin, ModelForm):
    """
    Form for adding an account which includes all fields available.

    TODO: status field
    """
#    twitter = forms.CharField(label=_('Twitter'), required=False, max_length=100,
#        widget=forms.TextInput(attrs={
#            'class': 'mws-textinput',
#            'placeholder': _('Twitter profile')
#    }))
#
#    linkedin = forms.CharField(label=_('LinkedIn'), required=False, max_length=100,
#        widget=forms.TextInput(attrs={
#            'class': 'mws-textinput',
#            'placeholder': _('LinkedIn profile')
#    }))
#
#    facebook = forms.URLField(label=_('Facebook'), required=False,
#        widget=forms.TextInput(attrs={
#            'class': 'mws-textinput',
#            'placeholder': _('Facebook profile link')
#    }))

    primary_website = forms.URLField(label=_('Primary website'), initial='http://', required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput tabbable',
            'placeholder': 'http://'
    }))
    
    # TODO: add e-mailadres check
    #        if cleaned_data.get('email'):
    #            if Account.objects.filter(email_addresses__email_address__iexact=cleaned_data.get('email')).exists():
    #                self._errors['email'] = self.error_class([_('E-mail address already in use.')])

    def is_valid(self):
        """
        Overloading super().is_valid to also validate all formsets.
        """
        is_valid = super(AddAccountForm, self).is_valid()

        # Check e-mail addresses
        for form in self.email_addresses_formset:
            if not form.is_valid():
                is_valid = False

        # Check phone numbers
        for form in self.phone_numbers_formset:
            if not form.is_valid():
                is_valid = False

        # Check addresses
        for form in self.addresses_formset:
            if not form.is_valid():
                is_valid = False

        # Check websites
        for form in self.websites_formset:
            if not form.is_valid():
                is_valid = False

        return is_valid

    class Meta:
        model = Account
#        fields = ('name', 'tags', 'twitter', 'facebook', 'linkedin', 'description')
        fields = ('name', 'description' , 'legalentity', 'taxnumber', 'bankaccountnumber', 'cocnumber', 'iban', 'bic')

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput required tabbable',
                'placeholder': _('Company name'),
            }),
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '3',
                'class': 'tabbable',
                'placeholder': _('Description'),
            }),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),

        }


class EditAccountForm(TagsFormMixin, ModelForm):
    """
    Form for editing an existing account which includes all fields available.

    TODO: status field
    """
#    twitter = forms.CharField(label=_('Twitter'), required=False, max_length=100,
#        widget=forms.TextInput(attrs={
#            'class': 'mws-textinput',
#            'placeholder': _('Twitter username')
#    }))
#
#    linkedin = forms.URLField(label=_('Facebook'), required=False,
#        widget=forms.TextInput(attrs={
#            'class': 'mws-textinput',
#            'placeholder': _('LinkedIn profile link')
#    }))
#
#    facebook = forms.CharField(label=_('LinkedIn'), required=False, max_length=100,
#        widget=forms.TextInput(attrs={
#            'class': 'mws-textinput',
#            'placeholder': _('Facebook username')
#    }))

    primary_website = forms.URLField(label=_('Primary website'), initial='http://', required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput tabbable',
            'placeholder': 'http://'
    }))

    def __init__(self, user=None, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):

        super(EditAccountForm, self).__init__(data, files, auto_id, prefix,
                 initial, error_class, label_suffix,
                 empty_permitted, instance)

        # Provide initial data for primary website
        try:
            self.fields['primary_website'].initial = Website.objects.filter(account=self.instance, is_primary=True)[0].website
        except Exception:
            pass

#        # Try providing initial social media
#        try:
#            self.fields['twitter'].initial = self.instance.social_media.filter(name='twitter')[0].username
#        except Exception:
#            pass
#        try:
#            self.fields['linkedin'].initial = self.instance.social_media.filter(name='linkedin')[0].profile_url
#        except:
#            pass
#        try:
#            self.fields['facebook'].initial = self.instance.social_media.filter(name='facebook')[0].username
#        except:
#            pass

    def is_valid(self):
        """
        Overloading super().is_valid to also validate all formsets.
        """
        is_valid = super(EditAccountForm, self).is_valid()

        # Check e-mail addresses
        for form in self.email_addresses_formset:
            if not form.is_valid():
                is_valid = False

        # Check phone numbers
        for form in self.phone_numbers_formset:
            if not form.is_valid():
                is_valid = False

        # Check addresses
        for form in self.addresses_formset:
            if not form.is_valid():
                is_valid = False

        # Check websites
        for form in self.websites_formset:
            if not form.is_valid():
                is_valid = False

        return is_valid

    class Meta:
        model = Account
#        fields = ('name', 'tags', 'twitter', 'facebook', 'linkedin', 'website', 'description')
        fields = ('name', 'description' , 'legalentity', 'taxnumber', 'bankaccountnumber', 'cocnumber', 'iban', 'bic')

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput required tabbable',
                'placeholder': _('Company name'),
            }),
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '3',
                'class': 'tabbable',
                'placeholder': _('Description'),
            }),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),
        }


class WebsiteBaseForm(ModelForm):
    website = forms.URLField(max_length=30, initial='http://',
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput tabbable',
            'placeholder': 'http://'
    }))

    class Meta:
        model = Website
        exclude = ('account')
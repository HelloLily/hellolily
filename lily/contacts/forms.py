from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.utils.functions import autostrip
from lily.utils.models import EmailAddress


class AddContactMinimalForm(ModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    account = forms.ModelChoiceField(label=_('Works at'), required=False,
                                     queryset=Account.objects.all(),
                                     empty_label=_('Select an account'),
                                     widget=forms.Select(attrs={'class': 'chzn-select'}))

    email = forms.EmailField(label=_('E-mail'), max_length=255, required=False,
        widget=forms.TextInput(attrs={
        'class': 'mws-textinput',
        'placeholder': _('E-mail address')
    }))

    phone = forms.CharField(max_length=40, required=False,
        widget=forms.TextInput(attrs={
            'class': 'mws-textinput',
            'placeholder': _('Phone number')
    }))

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'auto_id':'id_contact_quickbutton_%s'
        })
        super(AddContactMinimalForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddContactMinimalForm, self).clean()

        # check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        if cleaned_data.get('email'):
            try:
                EmailAddress.objects.get(email_address=cleaned_data.get('email'))
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])
            except EmailAddress.DoesNotExist:
                pass
            except EmailAddress.MultipleObjectsReturned:
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])

        return cleaned_data

    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'email', 'phone')

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mws-textinput required',
                'placeholder': _('First name'),
            }),
            'preposition': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Preposition'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mws-textinput',
                'placeholder': _('Last name'),
            }),
        }

class AddContactForm(ModelForm):
    """
    Form to add a contact which all fields available.
    """
    account = forms.ModelChoiceField(label=_('Works at'), required=False,
                                     queryset=Account.objects.all(),
                                     empty_label=_('Select an account'),
                                     widget=forms.Select(attrs={'class': 'chzn-select tabbable'}))

    def clean(self):
        """
        Form validation: fill in at least first or last name.
        """
        cleaned_data = super(AddContactForm, self).clean()

        # check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        return cleaned_data

    def is_valid(self):
        """
        Overloading super().is_valid to also validate all formsets.
        """
        is_valid = super(AddContactForm, self).is_valid()

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

        return is_valid

    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'gender', 'title', 'description', 'salutation')

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mws-textinput required tabbable',
                'placeholder': _('First name'),
            }),
            'preposition': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Preposition'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Last name'),
            }),
            'gender': forms.Select(attrs={
                'class': 'mws-textinput chzn-select-no-search tabbable',
            }),
            'title': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Title'),
            }),
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '3',
                'class': 'tabbable',
                'placeholder': _('Description'),
            }),
            'salutation': forms.Select(attrs={
                'class': 'mws-textinput chzn-select-no-search tabbable',
            })
        }


class EditContactForm(ModelForm):
    """
    Form for editing an existing contact which includes all fields available.
    """
#    edit_accounts = forms.BooleanField(required=False, label=_('Edit these next to provide more information'),
#        widget=forms.CheckboxInput())

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

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):

        super(EditContactForm, self).__init__(data, files, auto_id, prefix, initial, error_class,
                                              label_suffix, empty_permitted, instance)

        # Add field to select accounts where this contact works or has worked at.
#        self.fields['accounts'] = forms.ModelMultipleChoiceField(required=False,
#            queryset=Account.objects.all(),
#            initial=Account.objects.filter(pk__in=Function.objects.filter(contact=instance).values('account_id')),
#            widget=forms.SelectMultiple(attrs={ 'class': 'chzn-select' })
#        )

        # Try providing initial account info
        is_working_at = Function.objects.filter(contact=instance).values_list('account_id', flat=True)
        if len(is_working_at) == 1:
            # Add field to select account where this contact is working at.
            self.fields['account'] = forms.ModelChoiceField(label=_('Works at'), required=False,
                queryset=Account.objects.all(), initial=is_working_at[0],
                empty_label=_('Select an account'),
                widget=forms.Select(attrs={'class': 'chzn-select tabbable'}))
        else:
            # Add field to select account where this contact is working at.
            self.fields['account'] = forms.ModelChoiceField(label=_('Works at'), required=False,
                queryset=Account.objects.all(), empty_label=_('Select an account'),
                widget=forms.Select(attrs={'class': 'chzn-select tabbable'}))
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
        is_valid = super(EditContactForm, self).is_valid()

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

        return is_valid

    def clean(self):
        """
        Form validation: fill in at least first or last name.
        """
        cleaned_data = super(EditContactForm, self).clean()

        # check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        return cleaned_data

    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'gender', 'title', 'description', 'salutation')

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mws-textinput required tabbable',
                'placeholder': _('First name'),
            }),
            'preposition': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Preposition'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Last name'),
            }),
            'gender': forms.Select(attrs={
                'class': ' tabbable chzn-select-no-search'
            }),
            'title': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Title'),
            }),
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '3',
                'class': 'tabbable',
                'placeholder': _('Description'),
            }),
            'salutation': forms.Select(attrs={
                'class': 'tabbable chzn-select-no-search'
            }),
        }


class EditFunctionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditFunctionForm, self).__init__(*args, **kwargs)

        # Make all fields not required
        for key, field in self.fields.iteritems():
            self.fields[key].required = False

    def is_valid(self):
        """
        Overloading super().is_valid to validate all functions.
        """
        is_valid = super(EditFunctionForm, self).is_valid()

        # Validate formset
        for form in self.formset:
            if not form.is_valid():
                is_valid = False

        return is_valid


class FunctionForm(ModelForm):
    """
    Form to link contacts with accounts through functions.
    """

    def is_valid(self):
        """
        Overloading super().is_valid to also validate all formsets.
        """
        is_valid = super(FunctionForm, self).is_valid()

        # Check e-mail addresses
        for form in self.email_addresses_formset:
            if not form.is_valid():
                is_valid = False

        # Check phone numbers
        for form in self.phone_numbers_formset:
            if not form.is_valid():
                is_valid = False

        return is_valid

    class Meta:
        exclude = ('is_deleted', 'contact', 'email_addresses', 'phone_numbers')
        widgets = {
             'title': forms.TextInput(attrs={
                 'class': 'mws-textinput',
                 'placeholder': _('Function title')
             }),
             'department': forms.TextInput(attrs={
                 'class': 'mws-textinput',
                 'placeholder': _('Department')
             })
        }


# Enable autostrip input on these forms
AddContactMinimalForm = autostrip(AddContactMinimalForm)
AddContactForm = autostrip(AddContactForm)
EditContactForm = autostrip(EditContactForm)
EditFunctionForm = autostrip(EditFunctionForm)
FunctionForm = autostrip(FunctionForm)
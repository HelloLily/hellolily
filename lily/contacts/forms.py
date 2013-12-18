from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.tags.forms import TagsFormMixin


class AddContactQuickbuttonForm(ModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    account = forms.ModelChoiceField(label=_('Works at'), required=False,
                                     queryset=Account.objects.none(),
                                     empty_label=_('Select an account'))
    email = forms.EmailField(label=_('E-mail address'), max_length=255, required=False)
    phone = forms.CharField(label=_('Phone number'), max_length=40, required=False)

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_contact_quickbutton_%s'
        })

        super(AddContactQuickbuttonForm, self).__init__(*args, **kwargs)

        # Provide filtered query set
        self.fields['account'].queryset = Account.objects.all()

    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddContactQuickbuttonForm, self).clean()

        # Check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        # Prevent multiple contacts with the same e-mailadress when adding
        if cleaned_data.get('email'):
            if Contact.objects.filter(email_addresses__email_address__iexact=cleaned_data.get('email')).exists():
                self._errors['email'] = self.error_class([_('E-mail address already in use.')])

        return cleaned_data

    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'account', 'email', 'phone')


class CreateUpdateContactForm(TagsFormMixin, ModelForm):
    """
    Form to add a contact which all fields available.
    """
    account = forms.ModelChoiceField(label=_('Works at'), required=False,
                                     queryset=Account.objects.none(),
                                     empty_label=_('Select an account'))

    def __init__(self, *args, **kwargs):
        super(CreateUpdateContactForm, self).__init__(*args, **kwargs)

        # Provide filtered query set
        self.fields['account'].queryset = Account.objects.all()

        # Try providing initial account info
        try:
            is_working_at = Function.objects.filter(contact=self.instance).values_list('account_id', flat=True)
            if len(is_working_at) == 1:
                self.fields['account'].initial = is_working_at[0]
        except:
            pass

    def clean(self):
        """
        Form validation: fill in at least first or last name.
        """
        cleaned_data = super(CreateUpdateContactForm, self).clean()

        # Check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        return cleaned_data

    class Meta:
        model = Contact
        fields = ('salutation', 'gender', 'first_name', 'preposition', 'last_name', 'account', 'description')
        exclude = ('tags',)

        widgets = {
            'salutation': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'gender': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'description': forms.Textarea(attrs={
                'click_show_text': _('Add description')
            }),
        }

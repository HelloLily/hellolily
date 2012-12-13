from crispy_forms.layout import Layout, Hidden
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.tags.forms import TagsFormMixin
from lily.utils.forms import FieldInitFormMixin
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper, LilyFormHelper
from lily.utils.layout import Row, Column


class AddContactQuickbuttonForm(ModelForm, FieldInitFormMixin):
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
            'auto_id':'id_contact_quickbutton_%s'
        })
        
        super(AddContactQuickbuttonForm, self).__init__(*args, **kwargs)
        
        # Customize form layout
        self.helper = LilyFormHelper(self)
        self.helper.layout = Layout()
        self.helper.layout.insert(0, Hidden('submit_button', 'add', css_id='add-contact-submit'))
        self.helper.add_columns(
            Column('first_name', size=3, first=True),
            Column('preposition', size=1),
            Column('last_name', size=4),
            label=_('Name'),
        )
        self.helper.add_columns(
            Column('account', size=4, first=True),
        )
        self.helper.add_large_fields('email', 'phone')
        
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


class CreateUpdateContactForm(TagsFormMixin, ModelForm, FieldInitFormMixin):
    """
    Form to add a contact which all fields available.
    """
    account = forms.ModelChoiceField(label=_('Works at'), required=False,
                                     queryset=Account.objects.none(),
                                     empty_label=_('Select an account'))
    
    def __init__(self, *args, **kwargs):
        super(CreateUpdateContactForm, self).__init__(*args, **kwargs)
        
        # Customize form layout
        self.helper = DeleteBackAddSaveFormHelper(form=self)
        self.helper.layout.pop(0) # salutation
        self.helper.layout.pop(0) # gender
        self.helper.layout.pop(0) # first name
        self.helper.layout.pop(0) # preposition
        self.helper.layout.pop(0) # last name
        self.helper.layout.insert(0, 
            self.helper.create_multi_row(
                (
                    Column('salutation', size=2, first=True),
                    Column('gender', size=2),
                ),
                (
                    Column('first_name', size=3, first=True),
                    Column('preposition', size=1),
                    Column('last_name'),
                ),
                label=_('Name'),
            )
        )
        self.helper.replace('account',
            self.helper.create_columns(
                Column('account', first=True),
            ),
        )
        self.helper.wrap_by_names(Row, 'description', 'tags')
        
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

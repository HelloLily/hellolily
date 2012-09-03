from crispy_forms.layout import HTML, Layout
from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.cases.widgets import PrioritySelect
from lily.contacts.models import Contact
from lily.contacts.widgets import ContactAccountSelect
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper
from lily.utils.forms import FieldInitFormMixin
from lily.utils.layout import Row, Divider, Column, Div


class CreateUpdateCaseForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding or editing a case.
    """
    account = forms.ModelChoiceField(label=_('Account'), queryset=Account.objects.none(), 
        empty_label=_('an account'), required=False, widget=forms.Select(attrs={
        'class': 'contact_account',
    }))
    
    contact = forms.ModelChoiceField(label=_('Contact'), queryset=Account.objects.none(), 
        empty_label=_('a contact'), required=False, widget=ContactAccountSelect(attrs={
        'class': 'contact_account',
    }))
    
    assigned_to = forms.ModelChoiceField(label=_('Assigned to'), queryset=CustomUser.objects.none(),
        empty_label=None)
    
    def __init__(self, *args, **kwargs):
        """
        Create a dynamic layout and make accounts, contacts and users available for drop down selections. 
        """
        super(CreateUpdateCaseForm, self).__init__(*args, **kwargs)
        self.helper = DeleteBackAddSaveFormHelper(self)
        self.helper.layout = Layout()
        self.helper.add_columns(
            Column('priority', size=2, first=True),
        )
        self.helper.add_columns(
            Column('subject', first=True),
        )
        self.helper.layout.append(Row('description')),
        self.helper.add_columns(
            Column('status', size=2, first=True)
        )
        self.helper.add_columns(
            Column(Div(HTML(_('Select')), css_class='text-in-row'), size=1, first=True),
            Column('contact', size=3),
            Column(Div(HTML(_('and/or')), css_class='text-in-row center'), size=1),
            Column('account', size=3),
            label=_('Client'),
        )
        self.helper.add_columns(
            Column('assigned_to', first=True)
        )
        self.helper.insert_after(Divider, 'status', 'contact')
        
        # Provide filtered query set for account/contact/assigned_to
        self.fields['account'].queryset = Account.objects.all()        
        self.fields['contact'].queryset = Contact.objects.all()
        
        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using CustomUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the CustomUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        #
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant)
        self.fields['assigned_to'].initial = get_current_user()
    
    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(CreateUpdateCaseForm, self).clean()

        # Check if a contact or an account has been selected
        if not cleaned_data.get('contact') and not cleaned_data.get('account'):
            self._errors['contact'] = self._errors['account'] = self.error_class([_('Client can\'t be empty')])

        # Check if not both contact or an account have been selected or verify that an account the contact works at
        if cleaned_data.get('contact') and cleaned_data.get('account'):
            linked_account = existing_contact.get_primary_function().account
            if linked_account != cleaned_data.get('account'):
                self._errors['contact'] = self._errors['account'] = self.error_class([_('Choose either one')])

        return cleaned_data
    
    class Meta:
        model = Case
        fields = ('priority', 'subject', 'description', 'status', 'contact', 'account', 'assigned_to')
        exclude = ('is_deleted', 'closed_date', 'tenant')
        
        widgets = {
            'priority': PrioritySelect(attrs={ 
                'class': 'chzn-select-no-search',
            }),
            'description': forms.Textarea(attrs={
                'click_show_text': _('Add description'),
            }),
            'status': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }


class AddCaseQuickbuttonForm(CreateUpdateCaseForm):
    """
    Form that is used for adding a new Case through a quickbutton form.
    """
    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with 
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_case_quickbutton_%s',
        })
        
        super(AddCaseQuickbuttonForm, self).__init__(*args, **kwargs)
        self.helper.inputs = []
    
    class Meta:
        model = Case
        fields = ('priority', 'subject', 'description', 'status', 'contact', 'account', 'assigned_to')
        exclude = ('is_deleted', 'closed_date', 'tenant')
        
        widgets = {
            'priority': PrioritySelect(attrs={
                'class': 'chzn-select-no-search',
            }),
            'description': forms.Textarea(attrs={
                'click_and_show': False,
            }),
            'status': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }
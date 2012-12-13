from crispy_forms.layout import Layout
from django import forms
from django.conf import settings
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.deals.models import Deal
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser
from lily.utils.forms import FieldInitFormMixin
from lily.utils.formhelpers import DeleteBackAddSaveFormHelper
from lily.utils.layout import Column, Row


class CreateUpdateDealForm(ModelForm, FieldInitFormMixin):
    """
    Form for adding or editing a deal.
    """
    account = forms.ModelChoiceField(label=_('Account'), queryset=Account.objects.none(), 
        empty_label=_('Select an account'), widget=forms.Select())
    
    assigned_to = forms.ModelChoiceField(label=_('Assigned to'), queryset=CustomUser.objects.none(),
        empty_label=None, widget=forms.Select())
    
    expected_closing_date = forms.DateField(label=_('Expected closing date'), input_formats=settings.DATE_INPUT_FORMATS, 
        widget=forms.DateInput(format=settings.DATE_INPUT_FORMATS[0], 
            attrs={'class': 'expected_closing_date'}))
    
    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to make accounts available as assignees and add a form
        helper.
        """
        super(CreateUpdateDealForm, self).__init__(*args, **kwargs)
        self.helper = DeleteBackAddSaveFormHelper(self)
        self.helper.layout = Layout()
        self.helper.add_columns(
            Column('name', first=True),
        )
        self.helper.layout.append(Row('description')),
        self.helper.add_columns(
            Column('account', first=True),
        )
        self.helper.add_columns(
            Column('currency', size=2, first=True),
            Column('amount', size=2),
            label = self.fields['amount'].label,
        )
        self.helper.add_columns(
            Column('expected_closing_date', size=2, first=True)
        )
        self.helper.add_columns(
            Column('stage', size=2, first=True),
        )
        self.helper.add_columns(
            Column('assigned_to', first=True)
        )
        
        # Provide filtered query set
        self.fields['account'].queryset = Account.objects.all()
        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using CustomUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the CustomUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        #
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant)
        self.fields['assigned_to'].initial = get_current_user()
        
    class Meta:
        model = Deal
        fields = ('name', 'description', 'account', 'currency', 'amount', 'expected_closing_date', 'stage', 'assigned_to')
        exclude = ('is_deleted', 'closed_date', 'tenant')
        
        widgets = {
            'description': forms.Textarea(attrs={
                'click_show_text': _('Add description'),
            }),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'stage': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }


class AddDealQuickbuttonForm(CreateUpdateDealForm):
    """
    Form that is used for adding a new Deal through a quickbutton form.
    """
    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with 
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_deal_quickbutton_%s',
        })
        
        super(AddDealQuickbuttonForm, self).__init__(*args, **kwargs)
        self.helper.inputs = []
    
    class Meta:
        model = Deal
        fields = ('name', 'description', 'account', 'currency', 'amount', 'expected_closing_date', 'stage', 'assigned_to')
        exclude = ('is_deleted', 'closed_date', 'tenant')
        
        widgets = {
            'description': forms.Textarea(attrs={
                'click_and_show': False,
            }),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'stage': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }
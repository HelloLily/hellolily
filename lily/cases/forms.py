from datetime import datetime

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.cases.models import Case, CaseType
from lily.cases.widgets import PrioritySelect
from lily.contacts.models import Contact
from lily.tags.forms import TagsFormMixin
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import DatePicker, ShowHideWidget, AjaxSelect2Widget


class CreateUpdateCaseForm(TagsFormMixin, HelloLilyModelForm):
    """
    Form for adding or editing a case.
    """
    type = forms.ModelChoiceField(
        label=_('Type'),
        queryset=CaseType.objects,
        empty_label='---------',
        required=False,
    )

    account = forms.ModelChoiceField(
        label=_('Account'),
        required=False,
        queryset=Account.objects,
        empty_label=_('Select an account'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('json_account_list'),
            model=Account,
            filter_on='id_contact',
        ),
    )

    contact = forms.ModelChoiceField(
        label=_('Contact'),
        required=False,
        queryset=Contact.objects,
        empty_label=_('Select a contact'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('json_contact_list'),
            model=Contact,
            filter_on='id_account',
        ),
    )

    assigned_to = forms.ModelChoiceField(
        label=_('Assigned to'),
        queryset=CustomUser.objects,
        empty_label=None)

    expires = forms.DateField(
        label=_('Expires'),
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=DatePicker(
            options={
                'autoclose': 'true',
            },
            format=settings.DATE_INPUT_FORMATS[0],
            attrs={
                'placeholder': DatePicker.conv_datetime_format_py2js(settings.DATE_INPUT_FORMATS[0]),
            },
        )
    )

    def __init__(self, *args, **kwargs):
        """
        Set queryset and initial for *assign_to*
        """
        super(CreateUpdateCaseForm, self).__init__(*args, **kwargs)

        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using CustomUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the CustomUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        #
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant)
        self.fields['assigned_to'].initial = get_current_user()
        self.fields['expires'].initial = datetime.today()

    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(CreateUpdateCaseForm, self).clean()

        # Check if a contact or an account has been selected
        if not cleaned_data.get('contact') and not cleaned_data.get('account'):
            self._errors['contact'] = self._errors['account'] = self.error_class([_('Select a contact or account')])

        # Check if contact is selected combined with account
        if cleaned_data.get('contact') and not cleaned_data.get('account'):
            self._errors['contact'] = self._errors['account'] = self.error_class([_('When selecting contact you should also provide account')])

        # Check if not both contact or an account have been selected or verify that an account the contact works at
        if cleaned_data.get('contact') and cleaned_data.get('account'):
            linked_account = cleaned_data.get('contact').get_primary_function().account
            if linked_account != cleaned_data.get('account'):
                self._errors['contact'] = self._errors['account'] = self.error_class([_('Choose either one')])

        return cleaned_data

    class Meta:
        model = Case
        fields = (
            'status',
            'priority',
            'expires',
            'type',
            'subject',
            'description',
            'contact',
            'account',
            'assigned_to',
        )

        widgets = {
            'priority': PrioritySelect(attrs={
                'class': 'chzn-select-no-search',
            }),
            'description': ShowHideWidget(forms.Textarea({
                'rows': 3
            })),
            'status': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }


class CreateCaseQuickbuttonForm(CreateUpdateCaseForm):
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

        super(CreateCaseQuickbuttonForm, self).__init__(*args, **kwargs)

        self.fields['expires'].initial = datetime.today()
        self.fields['account'].widget.filter_on = 'id_case_quickbutton_contact'
        self.fields['contact'].widget.filter_on = 'id_case_quickbutton_account'

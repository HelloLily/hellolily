from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.cases.widgets import PrioritySelect
from lily.contacts.models import Contact
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import DatePicker, ShowHideWidget


class CreateUpdateCaseForm(HelloLilyModelForm):
    """
    Form for adding or editing a case.
    """
    account = forms.ModelChoiceField(label=_('Account'),
                                     queryset=Account.objects,
                                     empty_label=_('an account'),
                                     required=False,
                                     widget=forms.Select(attrs={
                                        'class': 'contact_account'
                                     }))

    contact = forms.ModelChoiceField(label=_('Contact'),
                                     queryset=Contact.objects,
                                     empty_label=_('a contact'),
                                     required=False)

    assigned_to = forms.ModelChoiceField(label=_('Assigned to'),
                                         queryset=CustomUser.objects.none(),
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

        # Check if not both contact or an account have been selected or verify that an account the contact works at
        if cleaned_data.get('contact') and cleaned_data.get('account'):
            linked_account = cleaned_data.get('contact').get_primary_function().account
            if linked_account != cleaned_data.get('account'):
                self._errors['contact'] = self._errors['account'] = self.error_class([_('Choose either one')])

        return cleaned_data

    class Meta:
        model = Case
        fields = ('priority', 'subject', 'description', 'status', 'contact', 'account', 'assigned_to', 'expires')
        exclude = ('is_deleted', 'closed_date', 'tenant')

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
        Overload super().__init__ to change auto_id to prevent clashing form field id's with
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_case_quickbutton_%s',
        })

        super(CreateCaseQuickbuttonForm, self).__init__(*args, **kwargs)

        self.fields['expires'].initial = datetime.today()

    class Meta:
        model = Case
        fields = ('priority', 'subject', 'description', 'status', 'contact', 'account', 'assigned_to', 'expires')
        exclude = ('is_deleted', 'closed_date', 'tenant')

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

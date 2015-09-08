from datetime import datetime

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.accounts.search import AccountMapping
from lily.contacts.models import Contact
from lily.contacts.search import ContactMapping
from lily.parcels.models import Parcel
from lily.tags.forms import TagsFormMixin
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyGroup, LilyUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import DatePicker, AjaxSelect2Widget

from .models import Case, CaseType, CaseStatus
from .widgets import PrioritySelect


class CreateUpdateCaseForm(TagsFormMixin, HelloLilyModelForm):
    """
    Form for adding or editing a case.
    """
    status = forms.ModelChoiceField(
        label=_('Status'),
        queryset=CaseStatus.objects,
        empty_label=_('Select a status'),
    )

    type = forms.ModelChoiceField(
        label=_('Type'),
        queryset=CaseType.objects,
        empty_label=_('Select a type'),
        required=True,
    )

    account = forms.ModelChoiceField(
        label=_('Account'),
        required=False,
        queryset=Account.objects,
        empty_label=_('Select an account'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('search_view'),
            model=Account,
            filter_on='%s,id_contact' % AccountMapping.get_mapping_type_name()
        ),
    )

    contact = forms.ModelChoiceField(
        label=_('Contact'),
        required=False,
        queryset=Contact.objects,
        empty_label=_('Select a contact'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('search_view'),
            model=Contact,
            filter_on='%s,id_account' % ContactMapping.get_mapping_type_name()
        ),
    )

    assigned_to_groups = forms.ModelMultipleChoiceField(
        label=_('Assigned to teams'),
        required=False,
        queryset=LilyGroup.objects,
        help_text='',
        widget=forms.SelectMultiple(attrs={
            'placeholder': _('Select one or more team(s)'),
        })
    )

    assigned_to = forms.ModelChoiceField(
        label=_('Assigned to'),
        queryset=LilyUser.objects,
        empty_label=_('Select a user'),
        required=False)

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

    parcel_provider = forms.ChoiceField(
        choices=Parcel.PROVIDERS,
        required=False,
        label=_('Parcel provider'),
    )

    parcel_identifier = forms.CharField(max_length=255, required=False, label=_('Parcel identifier'))

    is_archived = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        """
        Set queryset and initial for *assign_to*
        """
        super(CreateUpdateCaseForm, self).__init__(*args, **kwargs)

        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using LilyUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the LilyUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        user = get_current_user()
        self.fields['assigned_to'].queryset = LilyUser.objects.filter(tenant=user.tenant)
        self.fields['expires'].initial = datetime.today()

        # Pre-select users team if possible
        groups = user.lily_groups.all()
        if len(groups) == 1:
            self.fields['assigned_to_groups'].initial = groups

        # Setup parcel initial values
        self.fields['parcel_provider'].initial = Parcel.DPD
        self.fields['status'].initial = CaseStatus.objects.first()

        self.fields['type'].queryset = CaseType.objects.filter(is_archived=False)

        if self.instance.parcel is not None:
            self.fields['parcel_provider'].initial = self.instance.parcel.provider
            self.fields['parcel_identifier'].initial = self.instance.parcel.identifier

    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(CreateUpdateCaseForm, self).clean()

        contact = cleaned_data.get('contact')
        account = cleaned_data.get('account')

        # Check if a contact or an account has been selected
        if not contact and not account:
            self._errors['contact'] = self._errors['account'] = self.error_class([_('Select a contact or account')])

        # Verify that a contact works at selected account
        if contact and account and not account.functions.filter(contact__id=contact.id).exists():
            self._errors['contact'] = self._errors['account'] = self.error_class(
                [_('Selected contact doesn\'t work at account')]
            )

        return cleaned_data

    def save(self, commit=True):
        """
        Check for parcel information and store in separate model
        """
        if not self.instance.id:
            self.instance.created_by = get_current_user()

        instance = super(CreateUpdateCaseForm, self).save(commit=commit)

        # Add parcel information
        if self.cleaned_data['parcel_identifier'] and self.cleaned_data['parcel_provider']:
            # There is parcel information stored
            if instance.parcel:
                # Update
                instance.parcel.provider = self.cleaned_data['parcel_provider']
                instance.parcel.identifier = self.cleaned_data['parcel_identifier']
            else:
                # Create
                parcel = Parcel(
                    provider=self.cleaned_data['parcel_provider'],
                    identifier=self.cleaned_data['parcel_identifier']
                )
                if commit:
                    parcel.save()
                instance.parcel = parcel
        elif instance.parcel:
            # Remove parcel
            instance.parcel = None

        # If archived, set status to last position
        if instance.is_archived:
            instance.status = CaseStatus.objects.last()

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Case
        fieldsets = (
            (_('Who was it?'), {
                'fields': ('account', 'contact',),
            }),
            (_('What to do?'), {
                'fields': ('subject', 'description', 'type',),
            }),
            (_('Who is going to do this?'), {
                'fields': ('assigned_to_groups', 'assigned_to',),
            }),
            (_('When to do it?'), {
                'fields': ('status', 'priority', 'expires', 'is_archived',),
            }),
            (_('Parcel information'), {
                'fields': ('parcel_provider', 'parcel_identifier',)
            }),
        )

        widgets = {
            'priority': PrioritySelect(attrs={
                'class': 'chzn-select-no-search',
                'update-case-expire-date': '',
            }),
            'description': forms.Textarea({
                'rows': 3
            }),
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
        self.fields['account'].widget.filter_on = ('%s,id_case_quickbutton_contact' %
                                                   AccountMapping.get_mapping_type_name())
        self.fields['contact'].widget.filter_on = ('%s,id_case_quickbutton_account' %
                                                   ContactMapping.get_mapping_type_name())

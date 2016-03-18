import datetime

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.accounts.search import AccountMapping
from lily.tags.forms import TagsFormMixin
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import DatePicker, AjaxSelect2Widget

from .models import Deal, DealNextStep, DealWhyCustomer


class CreateUpdateDealForm(TagsFormMixin, HelloLilyModelForm):
    """
    Form for adding or editing a deal.
    """
    account = forms.ModelChoiceField(
        label=_('Account'),
        queryset=Account.objects,
        empty_label=_('Select an account'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('search_view'),
            filter_on=AccountMapping.get_mapping_type_name(),
            model=Account,
        ),
    )

    assigned_to = forms.ModelChoiceField(
        label=_('Assigned to'),
        queryset=LilyUser.objects,
        empty_label=None,
        widget=forms.Select()
    )

    next_step = forms.ModelChoiceField(
        label=_('Next step'),
        queryset=DealNextStep.objects,
        empty_label=_('Select the next step'),
    )

    next_step_date = forms.DateField(
        label=_('Next step date'),
        input_formats=settings.DATE_INPUT_FORMATS,
        required=False,
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

    why_customer = forms.ModelChoiceField(
        label=_('Why customer'),
        queryset=DealWhyCustomer.objects,
    )

    is_archived = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to make accounts available as assignees
        """
        super(CreateUpdateDealForm, self).__init__(*args, **kwargs)

        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using LilyUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the LilyUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        self.fields['assigned_to'].queryset = LilyUser.objects.filter(tenant=get_current_user().tenant)
        self.fields['assigned_to'].initial = get_current_user()

        self.fields['found_through'].required = True
        self.fields['contacted_by'].required = True

    def save(self, commit=True):
        instance = super(CreateUpdateDealForm, self).save(commit=commit)

        # Set closed_date after changing status to lost/won and reset it when it's new/pending.
        if instance.status.name in ['Won', 'Lost']:
            if not instance.closed_date:
                instance.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        else:
            instance.closed_date = None

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Deal

        fieldsets = (
            (_('Who is it?'), {
                'fields': ('account', 'is_archived', 'new_business', 'found_through', 'contacted_by', 'why_customer'),
            }),
            (_('What is it?'), {
                'fields': ('name', 'amount_once', 'amount_recurring', 'currency', 'description', 'quote_id'),
            }),
            (_('What\'s the status?'), {
                'fields': ('status', 'next_step', 'next_step_date', 'assigned_to'),
            }),
            (_('Action checklist'), {
                'fields': ('twitter_checked', 'is_checked', 'card_sent', 'feedback_form_sent'),
            }),
        )

        widgets = {
            'description': forms.Textarea({
                'rows': 3
            }),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'status': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }

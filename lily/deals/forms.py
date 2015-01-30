import datetime

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import utc
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.accounts.search import AccountMapping
from lily.deals.models import Deal
from lily.tags.forms import TagsFormMixin
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import DatePicker, ShowHideWidget, AjaxSelect2Widget, BootstrapRadioFieldRenderer


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

    expected_closing_date = forms.DateField(
        label=_('Expected closing date'),
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

    def save(self, commit=True):
        instance = super(CreateUpdateDealForm, self).save(commit=commit)

        # Set closed_date after changing stage to lost/won and reset it when it's new/pending
        if instance.stage in [Deal.WON_STAGE, Deal.LOST_STAGE]:
            instance.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        else:
            instance.closed_date = None

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Deal

        fieldsets = (
            (_('For who is it?'), {
                'fields': ('account', 'is_archived', 'new_business'),
            }),
            (_('What is it?'), {
                'fields': ('name', 'amount_once', 'amount_recurring', 'currency', 'description'),
            }),
            (_('What\'s the status?'), {
                'fields': ('stage', 'expected_closing_date', 'assigned_to', 'feedback_form_sent'),
            }),
        )

        widgets = {
            'description': forms.Textarea({
                'rows': 3
            }),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'stage': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'feedback_form_sent': forms.widgets.RadioSelect(renderer=BootstrapRadioFieldRenderer, attrs={
                'data-skip-uniform': 'true',
                'data-uniformed': 'true',
            }),
            'new_business': forms.widgets.RadioSelect(renderer=BootstrapRadioFieldRenderer, attrs={
                'data-skip-uniform': 'true',
                'data-uniformed': 'true',
            }),
        }


class CreateDealQuickbuttonForm(CreateUpdateDealForm):
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

        super(CreateDealQuickbuttonForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Deal
        fields = (
            'name',
            'description',
            'account',
            'currency',
            'amount_once',
            'amount_recurring',
            'expected_closing_date',
            'stage',
            'assigned_to',
        )

        widgets = {
            'description': ShowHideWidget(forms.Textarea(attrs={
                'rows': 3,
            })),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
            'stage': forms.Select(attrs={
                'class': 'chzn-select-no-search',
            }),
        }

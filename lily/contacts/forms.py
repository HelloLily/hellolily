from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.tags.forms import TagsFormMixin
from lily.utils.forms import HelloLilyModelForm
from lily.utils.functions import get_twitter_username_from_string, validate_linkedin_url
from lily.utils.forms.widgets import ShowHideWidget, BootstrapRadioFieldRenderer, AddonTextInput, AjaxSelect2Widget
from lily.utils.forms.mixins import FormSetFormMixin


class AddContactQuickbuttonForm(HelloLilyModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    account = forms.ModelChoiceField(
        label=_('Works at'),
        required=False,
        queryset=Account.objects.none(),
        empty_label=_('Select an account'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('json_account_list'),
            queryset=Account.objects.none(),
        ),
    )
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

    def clean_email(self):
        """
        Prevent multiple contacts with the same e-mailadress when adding
        """
        email = self.cleaned_data['email']
        if Contact.objects.filter(email_addresses__email_address__iexact=email).exists():
            raise ValidationError(
                _('E-mail address already in use.'),
                code='invalid',
            )

    def clean(self):
        """
        Form validation: all fields should be unique.
        """
        cleaned_data = super(AddContactQuickbuttonForm, self).clean()

        # Check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        return cleaned_data

    class Meta:
        model = Contact
        fields = ('first_name', 'preposition', 'last_name', 'account', 'email', 'phone')


class CreateUpdateContactForm(FormSetFormMixin, TagsFormMixin):
    """
    Form to add a contact which all fields available.
    """
    account = forms.ModelChoiceField(
        label=_('Works at'),
        required=False,
        queryset=Account.objects.none(),
        empty_label=_('Select an account'),
        widget=AjaxSelect2Widget(
            url=reverse_lazy('json_account_list'),
            queryset=Account.objects.none(),
        ),
    )

    twitter = forms.CharField(label=_('Twitter'), required=False, widget=AddonTextInput(icon_attrs={
        'class': 'icon-twitter',
        'position': 'left',
        'is_button': False
    }))
    linkedin = forms.URLField(label=_('LinkedIn'), required=False, widget=AddonTextInput(icon_attrs={
        'class': 'icon-linkedin',
        'position': 'left',
        'is_button': False
    }))

    def __init__(self, *args, **kwargs):
        super(CreateUpdateContactForm, self).__init__(*args, **kwargs)

        # Try providing initial account info
        is_working_at = Function.objects.filter(contact=self.instance).values_list('account_id', flat=True)
        if len(is_working_at) == 1:
            self.fields['account'].initial = is_working_at[0]

        self.fields['twitter'].initial = self.instance.get_twitter()
        self.fields['linkedin'].initial = self.instance.get_linkedin()

        self.fields['addresses'].form_attrs = {
            'exclude_address_types': ['visiting'],
            'extra_form_kwargs': {
                'initial': {
                    'type': 'home',
                }
            }
        }

    def clean_twitter(self):
        """
        Check if added twitter name is a valid twitter name
        """
        twitter = self.cleaned_data.get('twitter')
        if twitter:
            twitter_username = get_twitter_username_from_string(twitter)
            if not twitter_username:
                raise ValidationError(
                    _('Please enter a valid Twitter username'),
                    code='invalid',
                )
            return twitter_username

    def clean_linkedin(self):
        """
        Check if added linkedin url is a valid linkedin url
        """
        linkedin = self.cleaned_data['linkedin']

        if linkedin:
            if not validate_linkedin_url(linkedin):
                # Profile url was invalid
                raise ValidationError(
                    _('Please enter a valid LinkedIn profile url'),
                    code='invalid',
                )
            else:
                return linkedin

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
        fields = ('salutation', 'gender', 'first_name', 'preposition', 'last_name', 'account', 'description',
                  'email_addresses', 'phone_numbers', 'addresses', )
        widgets = {
            'description': ShowHideWidget(forms.Textarea(attrs={
                'rows': 3,
            })),
            'salutation': forms.widgets.RadioSelect(renderer=BootstrapRadioFieldRenderer, attrs={
                'data-skip-uniform': 'true',
                'data-uniformed': 'true',
            }),
            'gender': forms.widgets.RadioSelect(renderer=BootstrapRadioFieldRenderer, attrs={
                'data-skip-uniform': 'true',
                'data-uniformed': 'true',
            }),
        }

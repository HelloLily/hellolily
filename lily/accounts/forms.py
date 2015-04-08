import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from lily.socialmedia.connectors import Twitter
from lily.socialmedia.models import SocialMedia
from lily.tags.forms import TagsFormMixin
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.fields import FormSetField, TagsField
from lily.utils.forms.formsets import BaseFKFormSet
from lily.utils.forms.widgets import ShowHideWidget, AddonTextInput
from lily.utils.forms.mixins import FormSetFormMixin
from lily.utils.models.models import EmailAddress, Address

from .models import Account, Website


class AddAccountQuickbuttonForm(HelloLilyModelForm):
    """
    Form to add an account with the absolute minimum of information.
    """
    website = forms.URLField(
        label=_('Website'),
        max_length=255,
        initial='http://',
        required=False,
        widget=AddonTextInput(
            icon_attrs={'class': 'fa fa-magic'},
            button_attrs={'class': 'btn default dataprovider'},
            div_attrs={'class': 'input-group dataprovider'}
        )
    )
    name = forms.CharField(label=_('Company name'), max_length=255)
    emails = TagsField(label=_('E-mail addresses'), required=False)
    phone_number = forms.CharField(label=_('Phone number'), max_length=40, required=False)

    # Hidden field to hold JSON address data
    addresses = forms.CharField(max_length=1024, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        """
        Overload super().__init__ to change auto_id to prevent clashing form field id's with
        other forms.
        """
        kwargs.update({
            'auto_id': 'id_account_quickbutton_%s',
        })

        super(AddAccountQuickbuttonForm, self).__init__(*args, **kwargs)

    def clean_addresses(self):
        """
        Clean JSON Address field and create python array with address dicts.
        """
        try:
            json_addresses = json.loads(self.cleaned_data['addresses'])
        except ValueError:
            pass
        else:
            # Check addresses
            address_fields = [
                'street',
                'street_number',
                'complement',
                'city',
                'country',
                'postal_code'
            ]
            parsed_addresses = []
            for address in json_addresses:
                # For each address, only add fields that match Address fields
                address_data = {}
                for field, value in address.iteritems():
                    if field in address_fields:
                        address_data[field] = value
                if address_data:
                    parsed_addresses.append(address_data)
            return parsed_addresses

    def clean_name(self):
        """
        Prevent multiple accounts with the same company name
        """
        name = self.cleaned_data['name']
        if Account.objects.filter(name=name, is_deleted=False).exists():
                raise ValidationError(
                    _('Company name already in use.'),
                    code='invalid',
                )
        else:
            return name

    def clean_emails(self):
        """
        Prevent multiple accounts with the same e-mail adress when adding
        """
        for email in self.cleaned_data['emails']:
            validate_email(email)
            if Account.objects.filter(email_addresses__email_address__iexact=email, is_deleted=False).exists():
                raise ValidationError(
                    _('E-mail address already in use.'),
                    code='invalid',
                )

        return self.cleaned_data['emails']

    def clean_website(self):
        """
        Prevent multiple accounts with the same primary website when adding
        """
        website = self.cleaned_data['website']
        if Website.objects.filter(website=website, is_primary=True, account__is_deleted=False).exists():
            raise ValidationError(
                _('Website already in use.'),
                code='invalid',
            )
        else:
            return website

    def save(self, commit=True):
        """
        Save Many2Many email addresses to instance.
        """
        instance = super(AddAccountQuickbuttonForm, self).save(commit=commit)

        if commit:
            # Save email addresses
            first = True
            for email in self.cleaned_data['emails']:
                email_address = EmailAddress.objects.create(
                    email_address=email,
                    is_primary=first,
                    tenant=instance.tenant
                )
                instance.email_addresses.add(email_address)
                first = False

            # Save addresses
            for address in self.cleaned_data['addresses']:
                instance.addresses.add(Address.objects.create(**address))

        return instance

    class Meta:
        model = Account
        fields = (
            'website',
            'name',
            'description',
            'emails',
            'phone_number',
            'legalentity',
            'taxnumber',
            'bankaccountnumber',
            'cocnumber',
            'iban',
            'bic',
        )

        widgets = {
            'description': ShowHideWidget(forms.Textarea({
                'rows': 3,
            })),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),
        }


class WebsiteBaseForm(HelloLilyModelForm):
    """
    Base form for adding multiple websites to an account.
    """
    website = forms.URLField(max_length=255, initial='http://', required=False, label=_('Extra website(s)'))

    class Meta:
        model = Website
        fields = ('website',)


class CreateUpdateAccountForm(FormSetFormMixin, TagsFormMixin):
    """
    Form for creating or updating an account.
    """
    primary_website = forms.URLField(
        max_length=255,
        label=_('Primary website'),
        initial='http://',
        required=False,
        widget=AddonTextInput(
            icon_attrs={'class': 'fa fa-magic'},
            button_attrs={'class': 'btn default dataprovider'},
            div_attrs={'class': 'input-group dataprovider'}
        )
    )

    extra_websites = FormSetField(
        queryset=Website.objects,
        formset_class=modelformset_factory(
            Website,
            form=WebsiteBaseForm,
            formset=BaseFKFormSet,
            can_delete=True,
            extra=0
        ),
        template='accounts/formset_website.html',
        related_name='account',
    )

    twitter = forms.CharField(
        label=_('Twitter'),
        required=False,
        widget=AddonTextInput(
            icon_attrs={
                'class': 'fa fa-twitter',
                'position': 'left',
                'is_button': False
            }
        )
    )

    assigned_to = forms.ModelChoiceField(
        label=_('Assigned to'),
        queryset=LilyUser.objects,
        empty_label=_('Not assigned'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to set the initial value for the primary website if possible.
        Also set initial data for the websites field and set form_attrs for addresses formsetfield.
        """
        super(CreateUpdateAccountForm, self).__init__(*args, **kwargs)

        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using LilyUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the LilyUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        user = get_current_user()
        self.fields['assigned_to'].queryset = LilyUser.objects.filter(tenant=user.tenant)
        self.fields['assigned_to'].initial = user

        if self.instance.pk:
            self.fields['extra_websites'].initial = self.instance.websites.filter(is_primary=False)

            twitter = self.instance.social_media.filter(name='twitter').first()
            self.fields['twitter'].initial = twitter.username if twitter else ''

        self.fields['addresses'].form_attrs = {
            'extra_form_kwargs': {
                'initial': {
                    'country': 'NL',
                }
            }
        }

        # Provide initial data for primary website
        try:
            self.fields['primary_website'].initial = Website.objects.filter(
                account=self.instance,
                is_primary=True
            )[0].website
        except IndexError:
            pass

    def clean_twitter(self):
        """
        Check if added twitter name or url is valid.

        Returns:
            string: twitter username or empty string.
        """
        twitter = self.cleaned_data.get('twitter')

        if twitter:
            try:
                twit = Twitter(twitter)
            except ValueError:
                raise ValidationError(_('Please enter a valid username or link'), code='invalid')
            else:
                return twit.username
        return twitter

    def save(self, commit=True):
        """
        Save account to instance, and to database if commit is True.

        Returns:
            instance: an instance of the contact model
        """
        instance = super(CreateUpdateAccountForm, self).save(commit)

        if commit:
            twitter_input = self.cleaned_data.get('twitter')

            if twitter_input and instance.social_media.filter(name='twitter').exists():
                # There is input and there are one or more twitters connected, so we get the first of those.
                twitter_queryset = self.instance.social_media.filter(name='twitter')
                if self.fields['twitter'].initial:  # Only filter on initial if there is initial data.
                    twitter_queryset = twitter_queryset.filter(username=self.fields['twitter'].initial)
                twitter_instance = twitter_queryset.first()

                # And we edit it to store our new input.
                twitter = Twitter(self.cleaned_data.get('twitter'))
                twitter_instance.username = twitter.username
                twitter_instance.profile_url = twitter.profile_url
                twitter_instance.save()
            elif twitter_input:
                # There is input but no connected twitter, so we create a new one.
                twitter = Twitter(self.cleaned_data.get('twitter'))
                twitter_instance = SocialMedia.objects.create(
                    name='twitter',
                    username=twitter.username,
                    profile_url=twitter.profile_url,
                )
                instance.social_media.add(twitter_instance)
            else:
                # There is no input and zero or more connected twitters, so we delete them all.
                instance.social_media.filter(name='twitter').delete()

        return instance

    class Meta:
        model = Account

        fieldsets = (
            (_('Who was it?'), {
                'fields': (
                    'primary_website',
                    'name',
                    'description',
                    # Hidden fields
                    'legalentity',
                    'taxnumber',
                    'bankaccountnumber',
                    'cocnumber',
                    'iban',
                    'bic',
                ),
            }),
            (_('Who is handling the account?'), {
                'fields': ('assigned_to',),
            }),
            (_('Contact information'), {
                'fields': ('email_addresses', 'phone_numbers', 'addresses', 'extra_websites', ),
            }),
        )

        widgets = {
            'description': forms.Textarea({
                'rows': 3,
            }),
            'legalentity': forms.HiddenInput(),
            'taxnumber': forms.HiddenInput(),
            'bankaccountnumber': forms.HiddenInput(),
            'cocnumber': forms.HiddenInput(),
            'iban': forms.HiddenInput(),
            'bic': forms.HiddenInput(),
        }

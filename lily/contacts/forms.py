from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from lily.accounts.models import Account
from lily.accounts.search import AccountMapping
from lily.contacts.models import Contact, Function
from lily.socialmedia.connectors import Twitter, LinkedIn
from lily.socialmedia.models import SocialMedia
from lily.tags.forms import TagsFormMixin
from lily.utils.forms.mixins import FormSetFormMixin
from lily.utils.forms.widgets import ShowHideWidget, BootstrapRadioFieldRenderer, AddonTextInput, AjaxSelect2Widget


class CreateUpdateContactForm(FormSetFormMixin, TagsFormMixin):
    """
    Form to add a contact which all fields available.
    """
    account = forms.CharField(
        label=_('Works at'),
        required=False,
        help_text='',
        widget=AjaxSelect2Widget(
            tags=True,
            url=reverse_lazy('search_view'),
            filter_on=AccountMapping.get_mapping_type_name(),
            model=Account,
            attrs= {
                'class': 'select2ajax'
            }
        )
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

    linkedin = forms.CharField(
        label=_('LinkedIn'),
        required=False,
        widget=AddonTextInput(
            icon_attrs={
                'class': 'fa fa-linkedin',
                'position': 'left',
                'is_button': False
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super(CreateUpdateContactForm, self).__init__(*args, **kwargs)

        self.fields['account'].help_text = ''  # Fixed in django 1.8: now the help text is appended instead of overwritten

        if kwargs.get('initial', None):
            kwargs_initial = kwargs.get('initial', None)
            if kwargs_initial.get('account', None):
                self.fields['account'].initial = {kwargs_initial.get('account', None)}
                self.fields['account'].widget.data = self.fields['account'].initial

        if self.instance.pk:
            self.fields['account'].initial = [function.account for function in self.instance.functions.all()]
            self.fields['account'].widget.data = self.fields['account'].initial

            twitter = self.instance.social_media.filter(name='twitter').first()
            self.fields['twitter'].initial = twitter.username if twitter else ''

            linkedin = self.instance.social_media.filter(name='linkedin').first()
            self.fields['linkedin'].initial = linkedin.username if linkedin else ''

        self.fields['addresses'].form_attrs = {
            'exclude_address_types': ['visiting'],
            'extra_form_kwargs': {
                'initial': {
                    'type': 'home',
                    'country': 'NL',
                }
            }
        }

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

    def clean_linkedin(self):
        """
        Check if added linkedin url is a valid linkedin url.

        Returns:
            string: linkedin username or empty string.
        """
        linkedin = self.cleaned_data['linkedin']

        if linkedin:
            try:
                lin = LinkedIn(linkedin)
            except ValueError:
                raise ValidationError(_('Please enter a valid username or link'), code='invalid')
            else:
                return lin.username

        return linkedin

    def clean_account(self):
        account_ids = self.cleaned_data['account'].split(',')
        for i, account_id in enumerate(account_ids):
            try:
                account_ids[i] = int(account_id)
            except ValueError:
                account_ids[i] = 0

        return Account.objects.filter(pk__in=account_ids)

    def clean(self):
        """
        Form validation: fill in at least first or last name.

        Returns:
            dict: cleaned data of all fields.
        """
        cleaned_data = super(CreateUpdateContactForm, self).clean()

        # Check if at least first or last name has been provided.
        if not cleaned_data.get('first_name') and not cleaned_data.get('last_name'):
            self._errors['first_name'] = self._errors['last_name'] = self.error_class([_('Name can\'t be empty')])

        return cleaned_data

    def save(self, commit=True):
        """
        Save contact to instance, and to database if commit is True.

        Returns:
            instance: an instance of the contact model
        """
        instance = super(CreateUpdateContactForm, self).save(commit)

        if commit:
            account_input = self.cleaned_data.get('account')
            twitter_input = self.cleaned_data.get('twitter')
            linkedin_input = self.cleaned_data.get('linkedin')

            self.instance.functions.exclude(account__in=account_input).delete()
            function_list = [Function.objects.get_or_create(contact=self.instance, account=account)[0] for account in account_input]
            for function in function_list:
                self.instance.functions.add(function)

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

            if linkedin_input and instance.social_media.filter(name='linkedin').exists():
                # There is input and there are one or more linkedins connected, so we get the first of those.
                linkedin_instance = self.instance.social_media.filter(name='linkedin')
                if self.fields['linkedin'].initial:  # Only filter on initial if there is initial data.
                    linkedin_instance = linkedin_instance.filter(username=self.fields['linkedin'].initial)
                linkedin_instance = linkedin_instance.first()

                # And we edit it to store our new input.
                linkedin = LinkedIn(self.cleaned_data.get('linkedin'))
                linkedin_instance.username = linkedin.username
                linkedin_instance.profile_url = linkedin.profile_url
                linkedin_instance.save()
            elif linkedin_input:
                # There is input but no connected linkedin, so we create a new one.
                linkedin = LinkedIn(self.cleaned_data.get('linkedin'))
                linkedin_instance = SocialMedia.objects.create(
                    name='linkedin',
                    username=linkedin.username,
                    profile_url=linkedin.profile_url,
                )
                instance.social_media.add(linkedin_instance)
            else:
                # There is no input and zero or more connected twitters, so we delete them all.
                instance.social_media.filter(name='linkedin').delete()

        return instance

    class Meta:
        model = Contact
        fields = (
            'salutation',
            'gender',
            'first_name',
            'preposition',
            'last_name',
            'account',
            'description',
            'email_addresses',
            'phone_numbers',
            'addresses',
        )
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

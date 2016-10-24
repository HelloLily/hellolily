from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_password_strength.widgets import PasswordStrengthInput
from django_password_strength.widgets import PasswordConfirmationInput

from lily.socialmedia.connectors import Twitter, LinkedIn
from lily.socialmedia.models import SocialMedia
from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser
from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.widgets import AddonTextInput, AvatarInput


class UserProfileForm(HelloLilyModelForm):
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
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['picture'].help_text = 'Maximum picture size is 300kb.'
        if self.instance.pk:
            twitter = self.instance.social_media.filter(name='twitter').first()
            self.fields['twitter'].initial = twitter.username if twitter else ''
            linkedin = self.instance.social_media.filter(name='linkedin').first()
            self.fields['linkedin'].initial = linkedin.username if linkedin else ''

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

    def clean_picture(self):
        picture = self.cleaned_data['picture']

        if picture and picture.size > settings.LILYUSER_PICTURE_MAX_SIZE:
            raise ValidationError(_('File too large. Size should not exceed 300 KB.'), code='invalid')

        return picture

    def save(self, commit=True):
        """
        Save contact to instance, and to database if commit is True.

        Returns:
            instance: an instance of the contact model
        """
        instance = super(UserProfileForm, self).save(commit)

        if commit:
            twitter_input = self.cleaned_data.get('twitter')
            linkedin_input = self.cleaned_data.get('linkedin')

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
        model = LilyUser
        fieldsets = [
            (_('Personal information'), {
                'fields': [
                    'first_name',
                    'last_name',
                    'position',
                    'picture',
                ],
            }),
            (_('Contact information'), {
                'fields': [
                    'phone_number',
                    'twitter',
                    'linkedin',
                ],
            }),
            (_('Language and time'), {
                'fields': [
                    'language',
                    'timezone',
                ],
            }),
        ]

        widgets = {'picture': AvatarInput()}


class UserAccountForm(HelloLilyModelForm):
    old_password = forms.CharField(label=_('Current password'), widget=forms.PasswordInput())
    new_password1 = forms.CharField(label=_('New password'), widget=PasswordStrengthInput(), required=False)
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=PasswordConfirmationInput(confirm_with='new_password1'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserAccountForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = False
        self.fields['old_password'].help_text = '<a href="%s" tabindex="-1">%s</a>' % (
            reverse('password_reset'),
            unicode(_('Forgot your password?'))
        )

    def clean(self):
        cleaned_data = super(UserAccountForm, self).clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 or new_password2:
            if not new_password1 == new_password2:
                self._errors["new_password2"] = self.error_class([_('Your passwords don\'t match.')])

        return cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        logged_in_user = get_current_user()

        if not logged_in_user.check_password(old_password):
            self._errors["old_password"] = self.error_class([_('Password is incorrect.')])

        return old_password

    def save(self, commit=True):
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            logged_in_user = get_current_user()
            logged_in_user.set_password(new_password)
            logged_in_user.save()

        return super(UserAccountForm, self).save(commit)

    class Meta:
        model = LilyUser
        fieldsets = [
            (_('Change your email address'), {'fields': ['email', ], }),
            (_('Change your password'), {'fields': ['new_password1', 'new_password2', ], }),
            (_('Confirm your password'), {'fields': ['old_password', ], })
        ]

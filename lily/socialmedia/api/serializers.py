from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.api.nested.mixins import RelatedSerializerMixin
from lily.socialmedia.connectors import Twitter, LinkedIn

from ..models import SocialMedia


class SocialMediaSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    def validate_twitter(self, username, profile_url):
        """
        Check the validity of the twitter username and/or profile_url.
        """
        profile = Twitter(username=username, profile_url=profile_url)

        return profile.username, profile.profile_url

    def validate_linkedin(self, username, profile_url):
        """
        Check the validity of the linkedin username and/or profile_url.
        """
        profile = LinkedIn(username=username, profile_url=profile_url)

        return profile.username, profile.profile_url

    def validate(self, attrs):
        attrs = super(SocialMediaSerializer, self).validate(attrs)

        try:
            attrs['username'], attrs['profile_url'] = getattr(self, 'validate_%s' % attrs.get('name'))(
                username=attrs.get('username'),
                profile_url=attrs.get('profile_url')
            )
        except TypeError:
            error_msg = _('Please fill in username or profile url.')
            raise serializers.ValidationError({
                'username': error_msg,
                'profile_url': error_msg
            })
        except AttributeError:
            pass  # We have no custom validation function for this type of social media

        if not attrs.get('name') is 'other' and 'other_name' in attrs:
            # Other name is always empty if name is not 'other'
            del attrs['other_name']

        return attrs

    class Meta:
        model = SocialMedia
        fields = ('id', 'name', 'name_display', 'other_name', 'username', 'profile_url')


class RelatedSocialMediaSerializer(RelatedSerializerMixin, SocialMediaSerializer):
    pass

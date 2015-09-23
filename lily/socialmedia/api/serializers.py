from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import empty

from lily.socialmedia.connectors import LinkedIn
from lily.socialmedia.connectors import Twitter
from lily.utils.api.related.mixins import RelatedSerializerMixin

from ..models import SocialMedia


class SocialMediaSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    def validate_twitter(self, username, profile_url):
        """
        Check the validity of the twitter username and/or profile_url.
        """
        Twitter(url=profile_url, username=username)

    def validate_linkedin(self, username, profile_url):
        """
        Check the validity of the linkedin username and/or profile_url.
        """
        LinkedIn(url=profile_url, username=username)

    def validate(self, attrs):
        attrs = super(SocialMediaSerializer, self).validate(attrs)

        try:
            getattr(self, 'validate_%s' % attrs.get('name'))(username=attrs.get('username'), profile_url=attrs.get('profile_url'))
        except ValueError:
            error_msg = _('Invalid value for username or profile url.')
            raise serializers.ValidationError({
                'username': error_msg,
                'profile_url': error_msg
            })
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

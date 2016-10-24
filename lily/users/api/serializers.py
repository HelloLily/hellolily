from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.utils.api.serializers import RelatedWebhookSerializer

from ..models import Team, LilyUser
from lily.messaging.email.api.serializers import EmailAccountSerializer


class LilyUserSerializer(WritableNestedSerializer):
    """
    Serializer for the LilyUser model.
    """
    full_name = serializers.CharField(read_only=True)
    profile_picture = serializers.CharField(read_only=True)
    picture = serializers.ImageField(write_only=True, required=False)
    webhooks = RelatedWebhookSerializer(many=True, required=False, create_only=True)
    primary_email_account = EmailAccountSerializer(allow_null=True, required=False)

    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'primary_email_account',
            'position',
            'profile_picture',
            'picture',
            'is_active',
            'picture',
            'phone_number',
            'internal_number',
            'social_media',
            'language',
            # 'timezone',
            'teams',
            'webhooks',
        )

    def update(self, instance, validated_data):
        if self.instance.picture is validated_data.get('picture'):
            validated_data['picture'] = None

        validated_team_list = []

        if 'teams' in validated_data:
            validated_team_list = validated_data.pop('teams')

        user = super(LilyUserSerializer, self).update(instance, validated_data)

        if validated_team_list:
            # Remove all teams from a user instance to add them after the serializer.
            self.instance.teams.clear()

            # Add teams to user.
            for validated_team in validated_team_list:
                user.teams.add(validated_team)

        return user

    def validate_picture(self, value):
        if value and value.size > settings.LILYUSER_PICTURE_MAX_SIZE:
            raise serializers.ValidationError(_('File too large. Size should not exceed 300 KB.'))

        return value

    def to_internal_value(self, data):
        # Reverse foreign key relations don't work yet with the WritableNestedSerializer, so we manually retrieve
        # the primery email account from the initial data.
        internal_value = super(LilyUserSerializer, self).to_internal_value(data)
        primary_email_account = data.get('primary_email_account')

        if primary_email_account:
            internal_value.update({
                'primary_email_account': primary_email_account
            })

        return internal_value


class RelatedLilyUserSerializer(RelatedSerializerMixin, LilyUserSerializer):

    class Meta:
        model = LilyUser

        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
        )


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Team model.
    """
    users = RelatedLilyUserSerializer(many=True, source='active_users')

    class Meta:
        model = Team
        fields = (
            'id',
            'name',
            'users',
        )


class RelatedTeamSerializer(RelatedSerializerMixin, TeamSerializer):
    class Meta:
        model = Team
        fields = (
            'id',
            'name',
        )


class LilyUserTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for the LilyUser model.

    Only returns the user token
    """
    auth_token = serializers.CharField(read_only=True)

    class Meta:
        model = LilyUser
        fields = ('auth_token',)

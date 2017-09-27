from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.utils.timesince import timesince, timeuntil
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from user_sessions.models import Session
from user_sessions.templatetags.user_sessions import device

from lily.api.fields import CustomTimeZoneField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.utils.api.serializers import RelatedWebhookSerializer
from lily.utils.functions import has_required_tier

from ..models import Team, LilyUser, UserInfo, UserInvite
from lily.messaging.email.api.serializers import EmailAccountSerializer


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = (
            'id',
            'email_account_status',
        )


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvite
        fields = (
            'id',
            'first_name',
            'email',
        )


class LilyUserSerializer(WritableNestedSerializer):
    """
    Serializer for the LilyUser model.
    """
    password = serializers.CharField(write_only=True, required=False, max_length=128)
    password_confirmation = serializers.CharField(write_only=True, required=False, max_length=128)
    full_name = serializers.CharField(read_only=True)
    profile_picture = serializers.CharField(read_only=True)
    picture = serializers.ImageField(write_only=True, required=False)
    webhooks = RelatedWebhookSerializer(many=True, required=False, create_only=True)
    primary_email_account = EmailAccountSerializer(allow_null=True, required=False)
    timezone = CustomTimeZoneField(required=False)
    info = UserInfoSerializer(read_only=True)

    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'language',
            'info',
            'internal_number',
            'is_active',
            'password',
            'password_confirmation',
            'phone_number',
            'picture',
            'position',
            'primary_email_account',
            'profile_picture',
            'social_media',
            'timezone',
            'teams',
            'webhooks',
        )

    def validate_picture(self, value):
        if value and value.size > settings.LILYUSER_PICTURE_MAX_SIZE:
            raise serializers.ValidationError(_('File too large. Size should not exceed 300 KB.'))

        return value

    def validate_email(self, value):
        if self.instance:  # If there's an instance, it means we're updating.
            if not self.context['request'].user.pk == self.instance.pk:
                raise serializers.ValidationError(_('You can only alter the email of your own user.'))
        return value

    def validate_password(self, value):
        if self.instance:  # If there's an instance, it means we're updating.
            if not self.context['request'].user.pk == self.instance.pk:
                raise serializers.ValidationError(_('You can only alter the password of your own user.'))
        return make_password(value)

    def validate_password_confirmation(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(_('Invalid password.'))

        return value

    def create(self, validated_data):
        return super(LilyUserSerializer, self).create(validated_data)

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')
        email = attrs.get('email')
        webhooks = attrs.get('webhooks')

        if webhooks and not has_required_tier(2):
            raise PermissionDenied

        if self.instance:  # If there's an instance, it means we're updating.
            if password and not password_confirmation:
                raise serializers.ValidationError({
                    'password_confirmation': _(
                        'When changing passwords, you need to confirm with your current password.'
                    ),
                })

            if email and email != self.instance.email and not password_confirmation:
                raise serializers.ValidationError({
                    'password_confirmation': _(
                        'When changing email adresses, you need to confirm with your current password.'
                    ),
                })

        return super(LilyUserSerializer, self).validate(attrs)

    def update(self, instance, validated_data):
        if instance.picture is validated_data.get('picture'):
            validated_data['picture'] = None

        if 'is_active' in validated_data:
            if self.context.get('request').user.is_admin:
                is_active = validated_data.get('is_active')

                # Only continue if we're actually activating a user.
                if is_active != instance.is_active and is_active:
                    # Increment the plan's quantity.
                    instance.tenant.billing.update_subscription(1)
            else:
                raise PermissionDenied

        validated_team_list = None

        if 'teams' in validated_data:
            validated_team_list = validated_data.pop('teams')

        user = super(LilyUserSerializer, self).update(instance, validated_data)

        if validated_team_list is not None:
            # Remove all teams from a user instance to add them after the serializer.
            self.instance.teams.clear()

            # Add teams to user.
            for validated_team in validated_team_list:
                user.teams.add(validated_team)

        return user

    def save(self, **kwargs):
        if self.instance:
            old_password = self.instance.password
            instance = super(LilyUserSerializer, self).save(**kwargs)
            new_password = instance.password

            if old_password != new_password:
                # Django uses the password as part of the hash,
                # so if password's changed update the hash to prevent logout.
                update_session_auth_hash(self.context['request'], self.context['request'].user)

            return instance

        return super(LilyUserSerializer, self).save(**kwargs)

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
            'profile_picture',
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


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for User sessions.
    """
    device = serializers.SerializerMethodField()
    expires_in = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    # TODO: location will use geoip2, which was introduced in django 1.9, so add this field after upgrading.
    # location = serializers.SerializerMethodField()

    def get_device(self, obj):
        return device(obj.user_agent) if obj.user_agent else 'Unkown'

    def get_expires_in(self, obj):
        return timeuntil(obj.expire_date)

    def get_last_login(self, obj):
        return timesince(obj.last_activity)

    def get_is_current(self, obj):
        if obj.session_key == self.context['request'].session.session_key:
            return True

        return False

    class Meta:
        model = Session
        fields = (
            'session_key',
            'device',
            'expires_in',
            'last_login',
            'ip',
            'is_current',
            # 'location',
        )

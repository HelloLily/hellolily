import analytics
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django_otp import user_has_device
from django.utils.timesince import timesince, timeuntil
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from user_sessions.models import Session
from user_sessions.templatetags.user_sessions import device

from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.tenant.api.serializers import TenantSerializer
from lily.utils.api.serializers import RelatedWebhookSerializer
from lily.utils.functions import has_required_tier

from ..models import Team, LilyUser, UserInfo, UserInvite
from lily.messaging.email.api.serializers import EmailAccountSerializer


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = (
            'id',
            'registration_finished',
        )


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInvite
        fields = (
            'id',
            'first_name',
            'email',
        )


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Team model.
    """
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        users = []

        for user in obj.active_users():
            users.append({
                'id': user.id,
                'full_name': user.full_name,
            })

        return users

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


class LilyUserSerializer(WritableNestedSerializer):
    """
    Serializer for the LilyUser model.
    """
    password = serializers.CharField(write_only=True, required=False, max_length=128)
    password_confirmation = serializers.CharField(write_only=True, required=False, max_length=128)
    full_name = serializers.CharField(read_only=True)
    profile_picture = serializers.CharField(read_only=True)
    picture = serializers.ImageField(write_only=True, required=False, allow_null=True)
    webhooks = RelatedWebhookSerializer(many=True, required=False, create_only=True)
    primary_email_account = EmailAccountSerializer(allow_null=True, required=False)
    info = UserInfoSerializer(read_only=True)
    teams = RelatedTeamSerializer(many=True, required=False, assign_only=True)
    tenant = TenantSerializer(read_only=True)
    has_two_factor = serializers.SerializerMethodField()
    has_password = serializers.SerializerMethodField()

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
            'teams',
            'webhooks',
            'is_admin',
            'tenant',
            'has_two_factor',
            'has_password',
        )

    def __init__(self, instance=None, *args, **kwargs):
        super(LilyUserSerializer, self).__init__(instance, *args, **kwargs)

        request = kwargs.get('context', {}).get('request', None)

        if instance != request.user:
            # Only show the has_password field when the current user asks their user record.
            self.fields.pop('has_password')

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

    def get_has_two_factor(self, obj):
        if self.context.get('request'):
            user = self.context.get('request').user

            if user.is_admin:
                # Only admins are allowed to see the 2FA status.
                return user_has_device(obj)
            else:
                return None
        else:
            return None

    def get_has_password(self, obj):
        if self.context.get('request'):
            user = self.context.get('request').user

            if user == obj:
                return user.has_usable_password()

        return None

    def create(self, validated_data):
        return super(LilyUserSerializer, self).create(validated_data)

    def validate(self, data):
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        email = data.get('email')
        webhooks = data.get('webhooks')

        if webhooks and not has_required_tier(2):
            raise PermissionDenied

        # If there's an instance, it means we're updating.
        if self.instance:
            # Only validate the current password if the user has a usable_password.
            # Users with social auth don't have one, but they can set one.
            if self.instance.has_usable_password():
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

        return super(LilyUserSerializer, self).validate(data)

    def update(self, instance, validated_data):
        current_user = self.context.get('request').user

        if instance.picture is validated_data.get('picture'):
            validated_data['picture'] = None

        increment_users = False

        if 'is_active' in validated_data:
            if current_user.is_admin:
                is_active = validated_data.get('is_active')

                # Only continue if we're actually activating a user.
                if is_active != instance.is_active and is_active:
                    increment_users = True
            else:
                raise PermissionDenied

        if 'internal_number' in validated_data:
            internal_number = validated_data.get('internal_number')
            if internal_number:
                try:
                    user = LilyUser.objects.get(internal_number=internal_number, tenant=current_user.tenant)
                except (LilyUser.DoesNotExist, PermissionDenied):
                    pass
                else:
                    if current_user.is_admin:
                        # If an internal number is passed we want to clear it if
                        # there's already a user with that internal number.
                        user.internal_number = None
                        user.save()
                    else:
                        if current_user.id != instance.id:
                            raise PermissionDenied
                        elif internal_number != instance.internal_number:
                            raise serializers.ValidationError({
                                'internal_number': [_('Another user is already using this internal number.')]
                            })

                # Track changing internal number in Segment.
                analytics.track(instance.id, 'internal-number-updated', {
                    'internal_number_updated_by': current_user.id,
                    'type': 'Admin' if current_user.is_admin else 'User',
                })

        instance = super(LilyUserSerializer, self).update(instance, validated_data)

        # Increment after saving the user in case of errors.
        if increment_users:
            # Increment the plan's quantity.
            instance.tenant.billing.update_subscription(1)

        return instance

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


class BasicLilyUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    profile_picture = serializers.CharField(read_only=True)
    picture = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'language',
            'internal_number',
            'phone_number',
            'profile_picture',
            'picture',
        )


class RelatedLilyUserSerializer(RelatedSerializerMixin, serializers.ModelSerializer):
    profile_picture = serializers.CharField(read_only=True)

    class Meta:
        model = LilyUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'profile_picture',
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

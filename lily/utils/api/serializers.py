#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lily.accounts.api.validators import HostnameValidator
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.tags.models import Tag, TAGABLE_MODELS

from ..models.models import Address, EmailAddress, PhoneNumber, ExternalAppLink, Webhook


class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize phone numbers.
    """
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    def validate_number(self, value):
        phone_number = value

        if phone_number:
            phone_number = re.sub(r'[\+\(\)– -]', '', phone_number)

            if not phone_number.isdigit():
                raise ValidationError('Phone number may not contain any letters.')
        else:
            raise ValidationError('Phone number must be filled in.')

        return value

    class Meta:
        model = PhoneNumber
        fields = ('id', 'status_name', 'number', 'type', 'other_type', 'status',)


class RelatedPhoneNumberSerializer(RelatedSerializerMixin, PhoneNumberSerializer):
    """
    Serializer used to serialize phone numbers from reference of another serializer.
    """
    pass


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize addresses.
    """
    address = serializers.CharField(required=True)

    class Meta:
        model = Address
        fields = (
            'id',
            'address',
            'postal_code',
            'city',
            'state_province',
            'country',
            'country_display',
            'type',
        )


class RelatedAddressSerializer(RelatedSerializerMixin, AddressSerializer):
    """
    Serializer used to serialize addresses from reference of another serializer.
    """
    pass


class EmailAddressSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EmailAddress
        fields = ('id', 'email_address', 'status', 'status_name', 'is_active')


class RelatedEmailAddressSerializer(RelatedSerializerMixin, EmailAddressSerializer):
    """
    Serializer used to serialize email addresses from reference of another serializer.
    """
    pass


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize tags.
    """
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.filter(model__in=TAGABLE_MODELS),
                                                      write_only=True)
    object_id = serializers.IntegerField(write_only=True)

    def validate_name(self, value):
        return value.lower()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'content_type', 'object_id', 'last_used', )


class RelatedTagSerializer(RelatedSerializerMixin, TagSerializer):
    """
    Serializer used to serialize tags from reference of another serializer.
    """
    # We set required to False because, as a related serializer, we don't know the object_id yet during validation
    # of a POST request. The instance has not yet been created.
    object_id = serializers.IntegerField(required=False)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'content_type', 'object_id', 'last_used', )


class ExternalAppLinkSerializer(serializers.ModelSerializer):
    tenant_id = serializers.IntegerField()

    class Meta:
        model = ExternalAppLink
        fields = (
            'url',
            'name',
            'tenant_id',
        )


class RelatedExternalAppLinkSerializer(RelatedSerializerMixin, ExternalAppLinkSerializer):
    pass


class WebhookSerializer(serializers.ModelSerializer):
    url = serializers.CharField(required=True, max_length=255, validators=[HostnameValidator()])

    class Meta:
        model = Webhook
        fields = (
            'id',
            'url',
            'name',
        )


class RelatedWebhookSerializer(RelatedSerializerMixin, WebhookSerializer):
    pass

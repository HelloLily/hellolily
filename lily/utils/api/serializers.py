#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

from lily.tags.models import Tag, TAGABLE_MODELS
from lily.utils.api.related.mixins import RelatedSerializerMixin

from ..models.models import Address, EmailAddress, PhoneNumber


# TODO: Delete this serializer
class RelatedModelSerializer(serializers.ModelSerializer):

    def __init__(self, instance=None, data=empty, **kwargs):
        self.related_object = kwargs.pop('related_object', None)
        super(RelatedModelSerializer, self).__init__(instance, data, **kwargs)

    def create(self, validated_data):
        ModelClass = self.Meta.model
        instance = ModelClass.objects.create(**validated_data)
        return instance


# TODO: Delete this serializer
class RelatedFieldSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        obj = super(RelatedFieldSerializer, self).to_internal_value(data)

        is_deleted = data.get('is_deleted', False)

        if 'id' not in data and is_deleted:
            # New object but removed, don't do anything
            return {}
        else:
            obj.update({
                'is_deleted': data.get('is_deleted', False)
            })

        return obj


class OldPhoneNumberSerializer(RelatedFieldSerializer):
    id = serializers.IntegerField(required=False)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    number = serializers.CharField(read_only=True)

    def validate_raw_input(self, value):
        phone_number = value

        if phone_number:
            # Strip plus sign, parentheses and whitespace
            phone_number = re.sub('[\+\(\)\s]', '', phone_number)

            if not phone_number.isdigit():
                raise ValidationError('Phone number may not contain any letters.')
        else:
            raise ValidationError('Phone number must be filled in.')

        return value

    class Meta:
        model = PhoneNumber
        fields = ('id', 'status_name', 'number', 'raw_input', 'type', 'other_type', 'status',)


class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize phone numbers.
    """
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    number = serializers.CharField(read_only=True)

    def validate_raw_input(self, value):
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
        fields = ('id', 'status_name', 'number', 'raw_input', 'type', 'other_type', 'status',)


class RelatedPhoneNumberSerializer(RelatedSerializerMixin, PhoneNumberSerializer):
    """
    Serializer used to serialize phone numbers from reference of another serializer.
    """
    pass


class OldAddressSerializer(RelatedFieldSerializer):
    id = serializers.IntegerField(required=False)
    street = serializers.CharField(required=True)
    street_number = serializers.IntegerField(required=True, error_messages={'invalid': 'Please enter a number.'})

    class Meta:
        model = Address
        fields = (
            'id',
            'street',
            'street_number',
            'complement',
            'postal_code',
            'city',
            'state_province',
            'country',
            'type',
        )


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize addresses.
    """
    street = serializers.CharField(required=True)
    street_number = serializers.IntegerField(required=True, error_messages={'invalid': 'Please enter a number.'})

    class Meta:
        model = Address
        fields = (
            'id',
            'street',
            'street_number',
            'complement',
            'postal_code',
            'city',
            'state_province',
            'country',
            'type',
        )


class RelatedAddressSerializer(RelatedSerializerMixin, AddressSerializer):
    """
    Serializer used to serialize addresses from reference of another serializer.
    """
    pass


class OldEmailAddressSerializer(RelatedFieldSerializer):
    id = serializers.IntegerField(required=False)
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EmailAddress
        fields = ('id', 'status_name', 'email_address', 'status',)


class EmailAddressSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EmailAddress
        fields = ('id', 'email_address', 'status', 'status_name', )


class RelatedEmailAddressSerializer(RelatedSerializerMixin, EmailAddressSerializer):
    """
    Serializer used to serialize email addresses from reference of another serializer.
    """
    pass


class OldTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',)


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize tags.
    """
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.filter(model__in=TAGABLE_MODELS), write_only=True)
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'content_type', 'object_id', )


class RelatedTagSerializer(RelatedSerializerMixin, TagSerializer):
    """
    Serializer used to serialize tags from reference of another serializer.
    """
    # We set required to False because, as a related serializer, we don't know the object_id yet during validation
    # of a POST request. The instance has not yet been created.
    object_id = serializers.IntegerField(required=False)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'content_type', 'object_id',)

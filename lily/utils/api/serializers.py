from rest_framework import serializers
from rest_framework.fields import empty

from ..models.models import Address, EmailAddress, PhoneNumber


class RelatedModelSerializer(serializers.ModelSerializer):

    def __init__(self, instance=None, data=empty, **kwargs):
        self.related_object = kwargs.pop('related_object', None)
        super(RelatedModelSerializer, self).__init__(instance, data, **kwargs)

    def create(self, validated_data):
        ModelClass = self.Meta.model
        instance = ModelClass.objects.create(**validated_data)
        return instance


class PhoneNumberSerializer(RelatedModelSerializer):
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    number = serializers.CharField(read_only=True)

    def create(self, validated_data):
        instance = super(PhoneNumberSerializer, self).create(validated_data)
        self.related_object.phone_numbers.add(instance)
        return instance

    class Meta:
        model = PhoneNumber
        fields = ('id', 'status_name', 'number', 'raw_input', 'type', 'other_type', 'status',)


class AddressSerializer(RelatedModelSerializer):

    def create(self, validated_data):
        instance = super(AddressSerializer, self).create(validated_data)
        self.related_object.addresses.add(instance)
        return instance

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


class EmailAddressSerializer(RelatedModelSerializer):
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    def create(self, validated_data):
        instance = super(EmailAddressSerializer, self).create(validated_data)
        self.related_object.email_addresses.add(instance)
        return instance

    class Meta:
        model = EmailAddress
        fields = ('id', 'status_name', 'email_address', 'is_primary', 'status',)

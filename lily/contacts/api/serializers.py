from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.fields import SanitizedHtmlCharField
from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.socialmedia.api.serializers import RelatedSocialMediaSerializer
from lily.utils.api.serializers import (RelatedPhoneNumberSerializer, RelatedAddressSerializer,
                                        RelatedEmailAddressSerializer, RelatedTagSerializer)
from ..models import Contact


class ContactSerializer(WritableNestedSerializer):
    """
    Serializer for the contact model.
    """
    # Custom fields.
    description = SanitizedHtmlCharField()

    # Set non mutable fields.
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    # Related fields.
    phone_numbers = RelatedPhoneNumberSerializer(many=True, required=False, create_only=True)
    addresses = RelatedAddressSerializer(many=True, required=False, create_only=True)
    email_addresses = RelatedEmailAddressSerializer(many=True, required=False, create_only=True)
    social_media = RelatedSocialMediaSerializer(many=True, required=False, create_only=True)
    accounts = RelatedAccountSerializer(many=True, required=False)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)

    # Show string versions of fields.
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    salutation_display = serializers.CharField(source='get_salutation_display', read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id',
            'accounts',
            'addresses',
            'content_type',
            'created',
            'description',
            'email_addresses',
            'first_name',
            'full_name',
            'gender',
            'gender_display',
            'last_name',
            'modified',
            'phone_numbers',
            'salutation',
            'salutation_display',
            'social_media',
            'tags',
            'title',
        )

    def validate(self, data):
        if not isinstance(data, dict):
            data = {'id': data}

        # Check if we are related and if we only passed in the id, which means user just wants new reference.
        if not (len(data) == 1 and 'id' in data and hasattr(self, 'is_related_serializer')):
            if not self.partial:
                first_name = data.get('first_name', None)
                last_name = data.get('last_name', None)

                # Not just a new reference, so validate if contact is set properly.
                if not any([first_name, last_name]):
                    raise serializers.ValidationError({
                        'first_name': _('Please enter a valid first name.'),
                        'last_name': _('Please enter a valid last name.')
                    })

        return super(ContactSerializer, self).validate(data)


class RelatedContactSerializer(RelatedSerializerMixin, ContactSerializer):
    """
    Serializer for the contact model when used as a relation.
    """
    class Meta:
        model = Contact
        # Override the fields because we don't want related fields in this serializer.
        fields = (
            'id',
            'created',
            'modified',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'gender_display',
            'title',
            'description',
            'salutation',
            'salutation_display',
        )

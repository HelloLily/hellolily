from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


from lily.accounts.api.serializers import RelatedAccountSerializer
from lily.api.serializers import ContentTypeSerializer
from lily.socialmedia.api.serializers import RelatedSocialMediaSerializer
from lily.utils.api.related.mixins import RelatedSerializerMixin
from lily.utils.api.related.serializers import WritableNestedSerializer
from lily.utils.api.serializers import RelatedPhoneNumberSerializer, RelatedAddressSerializer, RelatedEmailAddressSerializer, RelatedTagSerializer
from ..models import Contact, Function


class ContactSerializer(WritableNestedSerializer):
    """
    Serializer for the contact model.
    """
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
            'id',
            'last_name',
            'modified',
            'phone_numbers',
            'preposition',
            'salutation',
            'salutation_display',
            'social_media',
            'tags',
            'title',
        )

    def validate(self, data):
        # Check if we are related and if we only passed in the id, which means user just wants new reference.
        if not (len(data) == 1 and 'id' in data and hasattr(self, 'is_related_serializer')):
            # Not just a new reference, so validate if contact is set properly.
            if not any([data.get('first_name', None), data.get('preposition', None), data.get('last_name', None)]):
                raise serializers.ValidationError({'last_name': _('Please enter a valid name.')})

        return super(ContactSerializer, self).validate(data)

    def _handle_accounts(self, instance, account_list, update=False):
        # Create new accounts.
        account_instances = self.fields['accounts'].create([a for a in account_list if not a.get('id')])
        # Update and link existing accounts.
        account_instances += self.fields['accounts'].update(instance, [a for a in account_list if a.get('id')])

        function_list = []
        for ai in account_instances:
            # ai is the account instance passed in the request.
            if ai not in instance.accounts.all():
                # The account instance is new, so we append a new function to the list to relate it to the contact.
                function_list.append(Function.objects.create(account=ai, contact=instance))
            else:
                # The account instance is existing, so we retrieve and add to the function list.
                function_list.append(Function.objects.get(account=ai, contact=instance))

        if update and not self.root.partial:
            instance.functions.exclude(id__in=[function.id for function in function_list]).delete()

        instance.functions.add(*function_list)

    def create(self, validated_data):
        account_list = validated_data.pop('accounts', None)

        with transaction.atomic():
            instance = super(ContactSerializer, self).create(validated_data)

            if account_list and not hasattr(self, 'is_related_serializer'):
                self._handle_accounts(instance, account_list)

        return instance

    def update(self, instance, validated_data):
        account_list = validated_data.pop('accounts', None)

        with transaction.atomic():
            instance = super(ContactSerializer, self).update(instance, validated_data)

            if not hasattr(self, 'is_related_serializer'):
                if account_list:
                    self._handle_accounts(instance, account_list, update=True)
                elif not self.root.partial:
                    self._handle_accounts(instance, [], update=True)

        return instance


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
            'preposition',
            'last_name',
            'full_name',
            'gender',
            'gender_display',
            'title',
            'description',
            'salutation',
            'salutation_display',
        )

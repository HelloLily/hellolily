from rest_framework import serializers

from lily.api.nested.mixins import RelatedSerializerMixin
from ..models.models import (EmailLabel, EmailAccount, EmailMessage, Recipient, EmailAttachment, EmailTemplate,
                             SharedEmailConfig, TemplateVariable, DefaultEmailTemplate)


class SharedEmailConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedEmailConfig
        fields = ('id', 'email_account', 'is_hidden')


class EmailLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLabel
        fields = ('id', 'account', 'label_type', 'label_id', 'name', 'unread')


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ('id', 'name', 'email_address')


class EmailAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='download_url', read_only=True)

    class Meta:
        model = EmailAttachment
        fields = ('id', 'inline', 'size', 'message', 'cid', 'name', 'url', )


class EmailMessageSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    sender = RecipientSerializer(many=False, read_only=True)
    received_by = RecipientSerializer(many=True, read_only=True)
    received_by_cc = RecipientSerializer(many=True, read_only=True)
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    labels = EmailLabelSerializer(many=True, read_only=True)
    sent_date = serializers.ReadOnlyField()

    class Meta:
        model = EmailMessage
        fields = (
            'id',
            'account',
            'labels',
            'sent_date',
            'body_html',
            'body_text',
            'received_by',
            'received_by_cc',
            'sender',
            'attachments',
            'read',
            'subject',
            'is_starred',
            'is_spam',
            'is_draft',
        )


class EmailAccountSerializer(serializers.ModelSerializer):
    email_address = serializers.ReadOnlyField()
    labels = EmailLabelSerializer(many=True, read_only=True)
    public = serializers.BooleanField()

    class Meta:
        model = EmailAccount
        fields = (
            'id',
            'email_address',
            'labels',
            'label',
            'public',
            'shared_with_users',
            'is_authorized',
        )


class RelatedEmailAccountSerializer(RelatedSerializerMixin, EmailAccountSerializer):
    class Meta:
        model = EmailAccount
        fields = (
            'id',
            'email_address',
            'label',
            'public',
            'is_authorized',
        )


class EmailTemplateSerializer(serializers.ModelSerializer):
    default_for = RelatedEmailAccountSerializer(many=True, assign_only=True)

    class Meta:
        model = EmailTemplate
        fields = (
            'id',
            'name',
            'subject',
            'body_html',
            'default_for',
        )

    def update(self, instance, validated_data):
        validated_default_for = set([pk['id'] for pk in validated_data.pop('default_for', {})])
        existing_default_for = set(instance.default_for.all().values_list('id', flat=True))
        user = self.context.get('request').user

        add_list = list(validated_default_for - existing_default_for)
        del_list = list(existing_default_for - validated_default_for)

        # Add new default email template relations.
        for add_pk in add_list:
            DefaultEmailTemplate.objects.create(
                user_id=user.pk,
                template_id=instance.pk,
                account_id=add_pk
            )

        if not self.partial:
            # If not partial then we need to delete the unreferenced default_for relations.
            DefaultEmailTemplate.objects.filter(
                user_id=user.pk,
                template_id=instance.pk,
                account_id__in=del_list
            ).delete()

        return super(EmailTemplateSerializer, self).update(instance, validated_data)


class TemplateVariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateVariable

        fields = (
            'id',
            'name',
            'text',
            'is_public',
            'owner',
        )

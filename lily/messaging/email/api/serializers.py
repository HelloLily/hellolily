from rest_framework import serializers

from lily.api.fields import DynamicQuerySetPrimaryKeyRelatedField
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
    def get_default_for_queryset(self, instance=None):
        """
        Filtered queryset method that is called for:
            - Fetching of currently related items.
            - Fetching all possible relatable items.

        This function is called once per instance in the list view, and once for the detail view.
        If we're creating a new email template or validating all possible relatable items, instance is None.

        Args:
            instance (EmailTemplate instance): the email template instance for which we want to fetch items.
        """
        if instance:
            queryset = EmailAccount.objects.filter(
                default_templates__template=instance,
                default_templates__user=self.context.get('request').user
            )
        else:
            queryset = EmailAccount.objects.all()
        return queryset

    default_for = DynamicQuerySetPrimaryKeyRelatedField(many=True, queryset=get_default_for_queryset)

    class Meta:
        model = EmailTemplate
        fields = (
            'id',
            'name',
            'subject',
            'body_html',
            'default_for',
        )

    def create(self, validated_data):
        default_for = validated_data.pop('default_for')
        instance = super(EmailTemplateSerializer, self).create(validated_data)

        for email_account_id in default_for:
            # Get defaults for this user for the email account and replace it if exists, if not create new.
            default_template, created = DefaultEmailTemplate.objects.get_or_create(
                account_id=email_account_id,
                user=self.context.get('request').user,
            )
            if created or default_template.template is not instance:
                # Make sure the default is alway this template instance.
                default_template.template = instance
                default_template.save()

        return instance

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        validated_default_for = set([obj.pk for obj in validated_data.pop('default_for', [])])
        existing_default_for = set(EmailAccount.objects.filter(
            default_templates__user=user,
            default_templates__template_id=instance.pk
        ).values_list('pk', flat=True))

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

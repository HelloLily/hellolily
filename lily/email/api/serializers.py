from rest_framework import serializers

from email_wrapper_lib.models.models import EmailAccount, EmailMessage, EmailDraft, EmailRecipient, EmailDraftAttachment


class EmailRecipientSerializer(serializers.ModelSerializer):
    """
    Serializer for the email recipient model.
    """

    class Meta:
        model = EmailRecipient
        fields = (
            'id',
            'name',
            'email_address',
            'raw_value',
        )


class EmailAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the email account model.
    """

    class Meta:
        model = EmailAccount
        fields = (
            'id',
            'username',
            'user_id',
            'provider_id',
            'subscription_id',
            'history_token',
            'page_token',
        )


class EmailMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the email message model.
    """

    class Meta:
        model = EmailMessage
        fields = (
            'id',
        )


class EmailDraftAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the email draft attachment model.
    """

    size = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    def get_size(self, obj):
        # return obj.file.size
        return 'bla'

    def get_content_type(self, obj):
        # return obj.file.content_type
        return 'test'

    class Meta:
        model = EmailDraftAttachment
        fields = (
            'id',
            'inline',
            'file',
            'size',
            'content_type',
        )


class EmailDraftSerializer(serializers.ModelSerializer):
    """
    Serializer for the email draft model.
    """

    recipients = EmailRecipientSerializer(many=True)
    attachments = EmailDraftAttachmentSerializer(many=True)

    class Meta:
        model = EmailDraft
        fields = (
            'id',
            'subject',
            'body_text',
            'body_html',
            'recipients',
            'account',
            'in_reply_to',
            'attachments',
        )

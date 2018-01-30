from rest_framework import serializers

from email_wrapper_lib.models import EmailAccount, EmailMessage, EmailRecipient


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

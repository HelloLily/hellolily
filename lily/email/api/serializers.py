from rest_framework import serializers

from email_wrapper_lib.models import EmailAccount


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

from django_filters.rest_framework import FilterSet

from email_wrapper_lib.models import EmailAccount, EmailMessage


class EmailAccountFilter(FilterSet):
    class Meta:
        model = EmailAccount
        fields = {
            'username': ['exact', ],
        }


class EmailMessageFilter(FilterSet):
    class Meta:
        model = EmailMessage
        fields = {
            'remote_id': ['exact', ],
        }
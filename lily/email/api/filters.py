from django_filters.rest_framework import FilterSet

from email_wrapper_lib.models import EmailAccount


class EmailAccountFilter(FilterSet):
    class Meta:
        model = EmailAccount
        fields = {
            'username': ['exact', ],
        }

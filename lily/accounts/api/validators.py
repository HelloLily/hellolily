import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from lily.accounts.models import Account


class HostnameValidator(RegexValidator):
    """
    Check if the given string is a valid hostname
    """
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )

    message = _('Please enter a valid URL.')


class DuplicateAccountName(object):
    instance = None

    def __call__(self, name):
        queryset = Account.objects.filter(name=name, is_deleted=False)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError(_('Company name already in use.'))

    def set_context(self, serializer_field):
        self.instance = serializer_field.parent.instance

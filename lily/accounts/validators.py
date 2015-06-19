from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .models import Account


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

from django.utils import six
from rest_framework import serializers
from rest_framework.compat import OrderedDict

from lily.tenant.middleware import get_current_user


class LilyPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def get_queryset(self):
        queryset = self.queryset.filter(tenant=get_current_user().tenant)
        return queryset

    @property
    def choices(self):
        return OrderedDict([
            (
                six.text_type(self.to_representation(item)),
                six.text_type(item)
            )
            for item in self.get_queryset()
        ])

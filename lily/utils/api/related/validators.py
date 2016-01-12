from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class BaseRelatedValidator(object):
    instance = None
    field_name = None
    error_messages = {}
    manager = None

    def set_context(self, serializer):
        self.serializer = serializer
        self.instance = serializer.root.instance

        if hasattr(serializer.parent, 'many'):
            self.many = True
            self.field_name = serializer.parent.source
            if self.instance:
                self.manager = getattr(self.instance, self.field_name)
            else:
                self.manager = self.serializer.Meta.model.objects
        else:
            self.many = False
            self.field_name = serializer.source
            self.manager = getattr(serializer.parent.Meta.model, self.field_name).get_queryset()


class CreateOnlyValidator(BaseRelatedValidator):
    """
    Validator used to disable assignment of existing objects as relations.
    """
    instance = None
    field_name = None
    error_messages = {
        'not_allowed': _('Referencing to objects with an id is not allowed.'),
        'not_valid': _('Only id\'s of linked objects are valid.')
    }

    def __call__(self, value):
        if 'id' in value:
            if self.instance is None:
                    raise serializers.ValidationError({'id': self.error_messages['not_allowed']})
            else:
                manager = getattr(self.instance, self.field_name)
                if not manager.filter(pk=value['id']).exists():
                    raise serializers.ValidationError({'id': self.error_messages['not_valid']})

    def set_context(self, serializer_field):
        self.instance = serializer_field.root.instance
        self.field_name = serializer_field.parent.source

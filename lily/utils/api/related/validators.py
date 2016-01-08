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
            self.manager = getattr(self.serializer.root.Meta.model, self.field_name).field.model.objects
        else:
            self.many = False
            self.field_name = serializer.source
            self.manager = getattr(serializer.parent.Meta.model, self.field_name).get_queryset()


class CreateOnlyValidator(BaseRelatedValidator):
    """
    Validator used to disable assignment of existing objects as relations.
    """
    error_messages = {
        'not_allowed': _('Referencing to objects with an id is not allowed.'),
        'not_valid': _('Only id\'s of linked objects are valid.')
    }

    def __call__(self, value):
        if 'id' in value:
            if self.instance is None:
                raise serializers.ValidationError({'id': self.error_messages['not_allowed']})
            elif not self.manager.filter(pk=value['id']).exists():
                raise serializers.ValidationError({'id': self.error_messages['not_valid']})


class AssignOnlyValidator(BaseRelatedValidator):
    """
    Validator used to force assignment of existing objects as relations.
    """
    error_messages = {
        'not_allowed': _('Updating and/or creating objects is not allowed. Please provide an id only.'),
        'not_valid': _('Only id\'s of existing objects are valid.'),
    }

    def __call__(self, value):
        if 'id' not in value or not len(value) == 1:
            # There was no id or there was more than just an id.
            raise serializers.ValidationError({'id': self.error_messages['not_allowed']})
        elif not self.manager.filter(pk=value['id']).exists():
            # The given id doesn't link to an existing object.
            raise serializers.ValidationError({'id': self.error_messages['not_valid']})

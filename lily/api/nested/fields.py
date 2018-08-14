from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import IntegerField, empty, SkipField


class RelatedPrimaryKeyField(IntegerField):
    """
    Field that validates primary key values for nested serializers.
    """

    def __init__(self, **kwargs):
        kwargs.update({'required': kwargs.pop('required', False)})

        super(RelatedPrimaryKeyField, self).__init__(**kwargs)

        self.default_error_messages.update({
            'does_not_exist': _('The id must point to an existing object.'),
            'nonmatching_id': _('The id must match that of the object being updated.'),
        })

    def to_internal_value(self, data):
        value = super(RelatedPrimaryKeyField, self).to_internal_value(data)

        # self.parent = The serializer on which this field is actually defined.
        # self.root = The serializer to which the API request was made.
        if self.parent is not self.root:
            # Field is called via a relational field reference.
            model_cls = self.parent.Meta.model

            try:
                obj = model_cls.objects.get(pk=value)
                # The id does exist in the database, check for is_deleted flag.
                if getattr(obj, 'is_deleted', False):
                    self.fail('does_not_exist')
            except ObjectDoesNotExist:
                # The id does not exist in the database.
                self.fail('does_not_exist')

            if not model_cls.objects.filter(pk=value).exists():
                # The id does not exist in the database.
                self.fail('does_not_exist')
            else:
                # The id does exist in the database, check for is_deleted flag.
                pass
        elif self.parent.instance is not None and value is not self.parent.instance.pk:
            # We are updating while the id is not the same as the object that's updated.
            self.fail('nonmatching_id')

        return value

    def run_validation(self, data=empty):
        """
        SkipField is not permitted for foreign key relations, so prevent skipping validation of this field.
        """
        try:
            return super(RelatedPrimaryKeyField, self).run_validation(data)
        except SkipField:
            if hasattr(self.parent.parent, 'many'):
                # It is possible that in the case of many to many there is no id necessary.
                raise
            else:
                # In the case of foreign key, the id is always required.
                self.fail('invalid')

from collections import OrderedDict

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, SkipField, set_value
from rest_framework.validators import UniqueTogetherValidator

from .fields import RelatedPrimaryKeyField
from .serializers import WritableNestedListSerializer
from .validators import CreateOnlyValidator


class RelatedSerializerMixin(object):
    """
    Mixin used for related model serializers.
    """
    create_only = False

    def __init__(self, create_only=False, instance=None, data=empty, **kwargs):
        assert not (kwargs.get('read_only', False) and create_only), 'May not set both `read_only` and `create_only`.'
        assert not (kwargs.get('many', False) and create_only), 'May not set `create_only` to True when `many` is False'

        if create_only:
            self.create_only = create_only
            self.validators.append(CreateOnlyValidator())

        id_field = getattr(self.Meta, 'id_field', RelatedPrimaryKeyField())
        self.fields['id'] = id_field

        super(RelatedSerializerMixin, self).__init__(instance=instance, data=data, **kwargs)

    @classmethod
    def many_init(cls, *args, **kwargs):
        cls.Meta.list_serializer_class = WritableNestedListSerializer

        return super(RelatedSerializerMixin, cls).many_init(*args, **kwargs)

    def to_internal_value(self, data):
        """
        Monkey patch the validate empty values function of the serializers fields. This way the validation that checks
        if fields are required also works on partial updates (PATCH) requests.
        """
        def custom_validate_empty_values(self, data):
            """
            The custom validate empty function that always checks for empty values, even on partial update.
            """
            if self.read_only:
                return (True, self.get_default())

            if data is empty:
                # The partial_update check is removed here.
                if self.required:
                    self.fail('required')
                return (True, self.get_default())

            if data is None:
                if not self.allow_null:
                    self.fail('null')
                return (True, None)

            return (False, data)

        if self.root.partial and 'id' not in data:
            for field in self.fields.values():
                # This is the actual monkey patching part.
                funcType = type(field.validate_empty_values)
                field.validate_empty_values = funcType(custom_validate_empty_values, field, field.__class__)

        if isinstance(data, dict) and 'id' in data:  # Set the instance so validators work properly
            try:
                self.instance = self.Meta.model.objects.get(pk=data.get('id'))
            except ObjectDoesNotExist:
                pass

            if not self.create_only and len(data) == 1:
                ret = OrderedDict()
                errors = OrderedDict()

                field = self.fields['id']
                validate_method = getattr(self, 'validate_id', None)

                primitive_value = field.get_value(data)
                try:
                    validated_value = field.run_validation(primitive_value)
                    if validate_method is not None:
                        validated_value = validate_method(validated_value)
                except ValidationError as exc:
                    errors[field.field_name] = exc.detail
                except DjangoValidationError as exc:
                    errors[field.field_name] = list(exc.messages)
                except SkipField:
                    pass
                else:
                    set_value(ret, field.source_attrs, validated_value)

                if errors:
                    raise ValidationError(errors)

                return ret

        model_cls = self.root.Meta.model
        instance = self.root.instance
        content_type = ContentType.objects.get_for_model(model_cls)

        generic_related_fields = [field.name for field in model_cls._meta.virtual_fields]

        if self.parent.field_name in generic_related_fields:
            data['content_type'] = content_type.pk

            if instance:
                data['object_id'] = instance.pk
            else:
                # Remove unique together validator because we are creating so it's always unique.
                self.validators = [validator for validator in self.validators if not isinstance(validator, UniqueTogetherValidator)]

        return super(RelatedSerializerMixin, self).to_internal_value(data)


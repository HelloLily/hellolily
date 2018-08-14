from collections import OrderedDict

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, SkipField, set_value
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueTogetherValidator

from lily.api.mixins import ValidateEverythingSimultaneouslyMixin
from .fields import RelatedPrimaryKeyField
from .serializers import WritableNestedListSerializer
from .validators import CreateOnlyValidator, AssignOnlyValidator


class RelatedSerializerMixin(ValidateEverythingSimultaneouslyMixin):
    """
    Mixin used for related model serializers.

    Args:
        create_only (boolean):  Only able to create new objects and update existing related objects.
                                This means non related existing objects are not a valid reference.
        assign_only (boolean):  Only able to assign existing objects.
                                This means every existing object is a valid reference.
    """
    is_related_serializer = True  # Some serializers behave differently in the save of a related object
    create_only = False
    extra_field_attrs = ['create_only', 'assign_only']

    def __init__(self, create_only=False, assign_only=False, instance=None, data=empty, **kwargs):
        super(RelatedSerializerMixin, self).__init__(instance=instance, data=data, **kwargs)
        allow_null = kwargs.get('allow_null', False)
        read_only = kwargs.get('read_only', False)
        many = kwargs.get('many', False)

        assert not (read_only and create_only), 'May not set both `read_only` and `create_only`.'
        assert not (read_only and assign_only), 'May not set both `read_only` and `assign_only`.'
        assert not (many and create_only), 'May not set `create_only` to True when `many` is False.'
        assert not (create_only and assign_only), 'May not set both `create_only` and `assign_only`.'
        assert not (allow_null and many), 'May not set both `allow_null` and `many`.'

        self.create_only = create_only
        if create_only:
            self.validators.append(CreateOnlyValidator())

        self.assign_only = assign_only
        if assign_only:
            self.validators.append(AssignOnlyValidator())

        id_field = getattr(self.Meta, 'id_field', RelatedPrimaryKeyField())
        self.fields['id'] = id_field

    @classmethod
    def many_init(cls, *args, **kwargs):
        cls.Meta.list_serializer_class = WritableNestedListSerializer

        return super(RelatedSerializerMixin, cls).many_init(*args, **kwargs)

    def to_internal_value_fields(self, data, fields=None):
        """
        This is basically a copy of the super.to_internal_value(), but we need the option to only use certain fields.
        """
        if not isinstance(data, dict):
            message = self.error_messages['invalid'].format(datatype=type(data).__name__)
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]})

        validated_values = OrderedDict()
        errors = OrderedDict()
        fields = fields or [
            field for field in self.fields.values() if (not field.read_only) or (field.default is not empty)
        ]

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
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
                set_value(validated_values, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return validated_values

    def to_internal_value(self, data):
        """
        If just the id is given, it means the request is an attempt to link a related instance. Then skip all
        validation except the validation of the id field. The id field checks if it's a valid link.

        Monkey patch the validate empty values function of the serializers fields. This way the validation that checks
        if fields are required also works on partial updates (PATCH) requests.

        For generic relations autofill the content_type_id and object_id and remove the unique_together validator on
        creates, because then it's always unique (false error).
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

        if isinstance(data, int):
            data = {'id': data}
        elif not isinstance(data, dict):
            message = self.error_messages['invalid'].format(datatype=type(data).__name__)
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]})

        # Store local reference to prevent looping multiple times to find the root (which is what self.root does).
        root = self.root

        if 'id' in data:
            # Set the instance so validators work properly.
            try:
                self.instance = self.Meta.model.objects.get(pk=data.get('id'))
            except ObjectDoesNotExist:
                pass

            if len(data) == 1:
                # Id is the only field in data, so it's a try to just link.
                # Get the id field so we can validate it. Skip validation of other fields.

                id_field = self.fields.get('id')
                return self.to_internal_value_fields(data, [
                    id_field,
                ])

        elif root.partial:
            # Partial update with no id, so check if everything is filled despite being a partial update.
            for field in self.fields.values():
                # This is the actual monkey patching part.
                func_type = type(field.validate_empty_values)
                field.validate_empty_values = func_type(custom_validate_empty_values, field, field.__class__)

        model_cls = root.Meta.model
        instance = root.instance
        content_type = ContentType.objects.get_for_model(model_cls)

        generic_related_fields = [field.name for field in model_cls._meta.private_fields]

        if self.parent.field_name in generic_related_fields:
            if model_cls in ['TimeLog', 'Note']:
                data['gfk_content_type'] = content_type.pk
            else:
                data['content_type'] = content_type.pk

            if instance:
                if model_cls in ['TimeLog', 'Note']:
                    data['gfk_object_id'] = instance.pk
                else:
                    data['object_id'] = instance.pk
            else:
                # Remove unique together validator because we are creating so it's always unique.
                self.validators = [
                    validator for validator in self.validators if not isinstance(validator, UniqueTogetherValidator)
                ]

        return self.to_internal_value_fields(data)

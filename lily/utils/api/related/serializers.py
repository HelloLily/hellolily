from collections import OrderedDict
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import get_validation_error_detail


class WritableNestedSerializer(serializers.ModelSerializer):
    """
    Generic implementation of saving related fields.

    Just put a related field serializer amongst the normal fields
    """
    def _separate_data(self, validated_data):
        generic_related_data = {}
        many_related_data = {}

        for field_name in validated_data.copy():  # Copy because a dict can't be modified during loop.
            # Check for generic relation fields.
            if field_name in [field.name for field in self.Meta.model._meta.virtual_fields]:
                generic_related_data.update({
                    field_name: validated_data.pop('%s' % field_name)
                })

            # Check for many to many fields.
            if field_name in [field.name for field in self.Meta.model._meta.many_to_many]:
                many_related_data.update({
                    field_name: validated_data.pop('%s' % field_name)
                })

        return validated_data, generic_related_data, many_related_data

    def create(self, validated_data):
        # Prepare all data for saving.
        non_related_data, generic_related_data, many_related_data = self._separate_data(validated_data)

        with transaction.atomic():
            instance = super(WritableNestedSerializer, self).create(non_related_data)

            # Do save of generic related fields
            for field_name, field_data in generic_related_data.items():
                serializer = self.fields[field_name]

                # Add the reference to the current object in the field data.
                for item in field_data:
                    content_type = ContentType.objects.get_for_model(instance)
                    item.update({
                        'content_type': content_type,
                        'object_id': instance.pk,
                    })

                serializer.create(field_data)

            # Do save of many to many related fields.
            for field_name, field_data in many_related_data.items():
                serializer = self.fields[field_name]
                related_instance_list = serializer.create([fd for fd in field_data if not fd.get('id')])
                related_instance_list += serializer.update(instance, [fd for fd in field_data if fd.get('id')])

                getattr(instance, field_name).add(*related_instance_list)

        return instance

    def update(self, instance, validated_data):
        # Prepare all data for saving.
        non_related_data, generic_related_data, many_related_data = self._separate_data(validated_data)

        with transaction.atomic():
            instance = super(WritableNestedSerializer, self).update(instance, non_related_data)

            # Do save of generic related fields
            for field_name, field_data in generic_related_data.items():
                # Add the reference to the current object in the field data.
                for item in field_data:
                    item.update({
                        'subject': instance,
                    })

                serializer = self.fields[field_name]
                related_instance_list = serializer.update(None, field_data)
                manager = getattr(instance, field_name)

                if not self.root.partial:
                    # It's a full update, so we replace all currently linked objects with the new objects.
                    manager.exclude(id__in=[obj.id for obj in related_instance_list]).delete()

            # Do save of many to many related fields
            for field_name, field_data in many_related_data.items():
                serializer = self.fields[field_name]
                related_instance_list = serializer.update(None, field_data)
                manager = getattr(instance, field_name)

                if not self.root.partial:
                    # It's a full update, so we replace all currently linked objects with the new objects.
                    manager.remove(*manager.exclude(id__in=[obj.id for obj in related_instance_list]))

                manager.add(*related_instance_list)

        return instance

    def run_validation(self, data=empty):
        """
        We patch this function because we want to see all the errors at once.
        """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        errors = OrderedDict()

        try:
            data = self.to_internal_value(data)
        except ValidationError as exc:
            errors.update(exc.detail)

        try:
            self.run_validators(data)
        except (ValidationError, DjangoValidationError) as exc:
            errors.update(get_validation_error_detail(exc))

        try:
            data = self.validate(data)
            assert data is not None, '.validate() should return the validated data'
        except (ValidationError, DjangoValidationError) as exc:
            errors.update(get_validation_error_detail(exc))

        if errors:
            raise ValidationError(errors)

        return data


class WritableNestedListSerializer(serializers.ListSerializer):
    """
    List serializer that can be used to enable nested updates
    """

    def update(self, instance, validated_data):
        instance_list = []

        for attrs in validated_data:
            pk = attrs.pop('id', None)

            if pk:
                instance = self.child.Meta.model.objects.get(pk=pk)
                obj = self.child.update(instance, attrs)
            else:
                obj = self.child.create(attrs)

            instance_list.append(obj)

        return instance_list

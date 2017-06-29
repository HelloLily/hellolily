from collections import OrderedDict
import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error

from lily.changes.models import Change


class ValidateEverythingSimultaneouslyMixin(object):
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
            errors.update(as_serializer_error(exc))

        try:
            data = self.validate(data)
            assert data is not None, '.validate() should return the validated data'
        except (ValidationError, DjangoValidationError) as exc:
            errors.update(as_serializer_error(exc))

        if errors:
            raise ValidationError(errors)

        return data


class ModelChangesMixin(object):
    def create(self, request, *args, **kwargs):
        response = super(ModelChangesMixin, self).create(request, *args, **kwargs)

        obj_id = response.data.get('id')
        content_type_id = response.data.get('content_type').get('id')
        content_type = ContentType.objects.get(pk=content_type_id)

        Change.objects.create(
            action='post',
            data=json.dumps(request.data),
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
        )

        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        action = 'patch' if partial else 'put'
        ignored_fields = ['modified', 'id']

        if not partial:
            # Store the old data so we can compare changes.
            serializer = self.get_serializer(instance=self.get_object())
            old_data = serializer.data

        response = super(ModelChangesMixin, self).update(request, *args, **kwargs)

        obj = self.get_object()
        serializer = self.get_serializer(instance=obj)
        new_data = serializer.data

        if not partial:
            data = {}
            # Compare old and new data and store those keys.
            diffkeys = [k for k in old_data if old_data.get(k) != new_data.get(k)]

            for key in diffkeys:
                if key in request.data:
                    value = request.data[key]

                    # PATCH usually just sends the ID, while PUT usually sends an object.
                    # For consistency we just want to store the ID.
                    if isinstance(value, dict) and len(value) == 1 and value.get('id'):
                        value = value.get('id')

                    data.update({key: value})
        else:
            data = request.data

        # Remove keys we don't want to track.
        for key in data.keys():
            if key in ignored_fields:
                del data[key]

        Change.objects.create(
            action=action,
            data=json.dumps(data),
            user=request.user,
            content_type=obj.content_type,
            object_id=obj.id,
        )

        return response

    @detail_route(methods=['get'])
    def changes(self, request, pk=None):
        obj = self.get_object()

        change_objects = Change.objects.filter(object_id=obj.id, content_type=obj.content_type)
        changes = []

        for change in change_objects:
            changes.append({
                'id': change.id,
                'action': change.action,
                'data': json.loads(change.data),
                'user': change.user.full_name,
                'created': change.created,
            })

        return Response({'changes': changes})

from collections import OrderedDict

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import as_serializer_error


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

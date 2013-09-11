from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, MultipleChoiceField

from lily.utils.functions import uniquify
from lily.utils.widgets import EmailProviderSelect


class MultipleInputAndChoiceField(MultipleChoiceField):
    """
    A subclass of MultipleChoiceField to allow new values being added to the otherwise
    fixed set of values.
    """
    empty_label = None

    def clean(self, value):
        """
        Overloading super().clean to allow submitting choices that don't exist in the given queryset.
        """
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])

        # Remove duplicate value, ignore case
        filter = lambda x: x.lower()
        uniquify(value, filter=filter)

        return value


class EmailProviderChoiceField(ModelChoiceField):
    """
    Subclassing ModelChoiceField to enable passing on actual instances to the
    default widget instead of just primary keys.
    """
    widget = EmailProviderSelect

    def prepare_value(self, value):
        return value

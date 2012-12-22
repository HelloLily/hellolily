from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField

from lily.utils.functions import uniquify


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
        uniquify(value, lambda x: x.lower())
        
        return value
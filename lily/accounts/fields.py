from django.core.exceptions import ValidationError
from django.forms.models import ModelMultipleChoiceField
from lily.utils.functions import uniquify

class MultipleInputAndChoiceField(ModelMultipleChoiceField):
    """
    A subclass of ModelMultipleChoiceField to not only support making relationships between models,
    but also to create new instances of a model to create a relationship with.
    """
    empty_label=None
    
    def clean(self, value):
        """
        Overloading super().clean to be able to submit a choice that's not in the given queryset.
        """
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])
        
        # Remove duplicate value, ignore case
        uniquify (value, lambda x: x.lower())
        
        return value
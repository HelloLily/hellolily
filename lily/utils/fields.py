from django.forms import ModelChoiceField, CharField

from lily.utils.widgets import EmailProviderSelect, TagInput


class TagsField(CharField):
    """
    The field used for selecting tags
    """
    widget = TagInput

    def __init__(self, choices=(), *args, **kwargs):
        super(TagsField, self).__init__(*args, **kwargs)
        self.choices = choices

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def to_python(self, value):
        value = super(TagsField, self).to_python(value)
        tags = value.split(',')

        # Remove "empty" tags to prevent adding empty tags for objects
        for i, tag in enumerate(reversed(tags)):
            if not tag:
                del tags[i]

        return tags


class EmailProviderChoiceField(ModelChoiceField):
    """
    Subclassing ModelChoiceField to enable passing on actual instances to the
    default widget instead of just primary keys.
    """
    widget = EmailProviderSelect

    def prepare_value(self, value):
        return value

from __future__ import unicode_literals

from collections import OrderedDict

from django.utils.encoding import force_text
from rest_framework.metadata import SimpleMetadata


class CustomMetaData(SimpleMetadata):
    def get_field_info(self, field):
        """
        Custom get field info so extra parameters of custom fields are displayed as well.
        """
        field_info = OrderedDict()
        field_info['type'] = self.label_lookup[field]
        field_info['required'] = getattr(field, 'required', False)

        attrs = ['read_only', 'label', 'help_text', 'min_length', 'max_length', 'min_value', 'max_value']

        # This is the custom part, load extra field attrs if necessary.
        if hasattr(field, 'extra_field_attrs'):
            attrs += field.extra_field_attrs

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != '':
                field_info[attr] = force_text(value, strings_only=True)

        if not field_info.get('read_only') and hasattr(field, 'choices'):
            field_info['choices'] = [{
                'value': choice_value,
                'display_name': force_text(choice_name, strings_only=True)
            } for choice_value, choice_name in field.choices.items()]

        return field_info

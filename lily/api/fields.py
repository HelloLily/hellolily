import re

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class RegexDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        if not data:
            raise ValidationError(_('This field is required'))

        # Regex to get the decimal value.
        regex = '([.,][0-9]{1,2}$)'
        data_split = re.split(regex, str(data))

        # Remove commas and periods.
        data = data_split[0].replace('.', '').replace(',', '')

        if len(data_split) >= 2:
            # Change comma to period for decimal separator.
            data += data_split[1].replace(',', '.')

        return data

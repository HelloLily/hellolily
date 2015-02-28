from django.forms import ModelChoiceField

from .widgets import EmailProviderSelect


class EmailProviderChoiceField(ModelChoiceField):
    """
    Subclassing ModelChoiceField to enable passing on actual instances to the
    default widget instead of just primary keys.
    """
    widget = EmailProviderSelect

    def prepare_value(self, value):
        return value

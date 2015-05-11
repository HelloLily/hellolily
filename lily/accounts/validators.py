from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Account


def duplicate_account_name(name):
    if Account.objects.filter(name=name, is_deleted=False).exists():
        raise ValidationError(
            _('Company name already in use.'),
            code='invalid',
        )

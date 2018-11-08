from django.conf import settings
from django.db import models

from lily.tenant.models import TenantMixin
from lily.utils.models.mixins import TimeStampedModel


def get_csv_import_upload_path(instance, filename):
    return settings.CSV_IMPORT_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'filename': filename
    }


class ImportUpload(TenantMixin, TimeStampedModel):
    """
    A class to hold an uploaded file to import contacts or accounts.
    """
    csv = models.FileField(
        upload_to=get_csv_import_upload_path,
        max_length=500
    )

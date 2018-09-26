from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser


def get_file_upload_path(instance, filename):
    return settings.OBJECT_FILE_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'content_type': instance.gfk_content_type.model,
        'object_id': instance.gfk_object_id,
        'filename': filename
    }


class ObjectFile(TenantMixin):
    """
    Allows files to be attached to an object.
    """
    file = models.FileField(upload_to=get_file_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    gfk_content_type = models.ForeignKey(ContentType)
    gfk_object_id = models.PositiveIntegerField()
    user = models.ForeignKey(LilyUser)

    class Meta:
        app_label = 'objectfiles'

    @property
    def name(self):
        return self.file.name.split('/')[-1]

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label="objectfiles", model="objectfile")

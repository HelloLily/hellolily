from django.db import models
from django_extensions.db.models import TimeStampedModel

from lily.tenant.models import TenantMixin
from lily.users.models import CustomUser


class BlogEntry(TenantMixin, TimeStampedModel):
    author = models.ForeignKey(CustomUser)
    content = models.CharField(max_length=255)
    reply_to = models.ForeignKey('self', blank=True, null=True)
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser


class TimeLog(TenantMixin):
    gfk_content_type = models.ForeignKey(ContentType)
    gfk_object_id = models.PositiveIntegerField()
    hours_logged = models.DecimalField(max_digits=7, decimal_places=3)
    user = models.ForeignKey(LilyUser)
    billable = models.BooleanField(default=False)
    date = models.DateTimeField()
    content = models.TextField(blank=True)

    def __unicode__(self):
        return '%sh logged for %s with ID %s' % (self.hours_logged, self.gfk_content_type.model, self.gfk_object_id)

    class Meta:
        ordering = ['-date']

from django.db import models
from django_extensions.db.models import TimeStampedModel

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser


class BlogEntry(TenantMixin, TimeStampedModel):
    author = models.ForeignKey(LilyUser)
    content = models.CharField(max_length=255)
    reply_to = models.ForeignKey('self', blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.content)
    
    def get_replies(self):
        return self.blogentry_set.all().order_by('-created')

from django.contrib.contenttypes.models import ContentType
from django.db import models

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser


class Change(TenantMixin):
    ACTION_CHOICES = (
        ('get', 'GET'),
        ('post', 'POST'),
        ('put', 'PUT'),
        ('patch', 'PATCH'),
    )

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    data = models.TextField()
    user = models.ForeignKey(LilyUser, related_name='object_changes')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'changes'

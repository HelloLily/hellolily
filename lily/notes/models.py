from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.tenant.models import TenantMixin
from lily.utils.models.mixins import DeletedMixin
from lily.users.models import LilyUser


NOTABLE_MODELS = ('account', 'contact', 'deal', 'case', 'call', 'callrecord')


class Note(TenantMixin, DeletedMixin):
    """
    Note model, simple text fields to store text about another model for everyone to see.
    """
    TYPE_NOTE, TYPE_CALL, TYPE_MEETUP = range(3)
    NOTE_TYPE_CHOICES = (
        (TYPE_NOTE, _('Note')),
        (TYPE_CALL, _('Call')),
        (TYPE_MEETUP, _('Meetup')),
    )

    content = models.TextField()
    author = models.ForeignKey(LilyUser)

    type = models.PositiveSmallIntegerField(choices=NOTE_TYPE_CHOICES, default=TYPE_NOTE)
    gfk_content_type = models.ForeignKey(ContentType)
    gfk_object_id = models.PositiveIntegerField()
    subject = GenericForeignKey('gfk_content_type', 'gfk_object_id')
    is_pinned = models.BooleanField(default=False)

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label='notes', model='note')

    def __unicode__(self):
        return self.content

    class Meta:
        ordering = ['-created']
        verbose_name = _('note')
        verbose_name_plural = _('notes')

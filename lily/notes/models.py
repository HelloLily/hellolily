from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _

from lily.utils.models import HistoryListItem
from lily.utils.models.mixins import DeletedMixin
from lily.users.models import LilyUser


class Note(HistoryListItem, DeletedMixin):
    """
    Note model, simple text fields to store text about another model for everyone to see.
    """
    content = models.TextField(verbose_name=_('note'))
    author = models.ForeignKey(LilyUser, verbose_name=_('author'))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    subject = generic.GenericForeignKey('content_type', 'object_id')

    def get_list_item_template(self):
        """
        Return the template that must be used for history list rendering
        """
        return 'notes/note_historylistitem.html'

    def save(self, *args, **kwargs):
        if self.sort_by_date is None:
            self.sort_by_date = self.created
        return super(Note, self).save()

    def __unicode__(self):
        return self.content

    class Meta:
        ordering = ['-sort_by_date']
        verbose_name = _('note')
        verbose_name_plural = _('notes')

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .fields import CreationDateTimeField, ModificationDateTimeField


class TimeStampMixin(object):
    """ TimeStampedModel
    An abstract base class model that provides self-managed "created" and "modified" fields.
    """
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    def save(self, **kwargs):
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super(TimeStampMixin, self).save(**kwargs)

    class Meta:
        abstract = True


class SoftDeleteMixin(object):
    """
    Deleted model, flags when an instance is deleted.
    """
    deleted = models.DateTimeField(_('deleted'), null=True, blank=True)
    is_deleted = models.BooleanField(_('is deleted'), default=False)

    def delete(self, using=None, hard=False):
        """
        Soft delete instance by flagging is_deleted as True.

        Arguments:
            using (str): which db to use
            hard (boolean): If True, permanent removal from db
        """
        if hard:
            super(SoftDeleteMixin, self).delete(using=using)
        else:
            self.is_deleted = True
            self.deleted = timezone.now()
            self.save()

    class Meta:
        abstract = True

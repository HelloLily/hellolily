from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_extensions.db.fields import ModificationDateTimeField
from django.utils.translation import ugettext_lazy as _

from lily.tenant.models import TenantMixin

TAGABLE_MODELS = ('account', 'contact', 'deal', 'case')


class Tag(TenantMixin):
    """
    Tag model, simple char field to store a tag. Is used to describe the model it is linked to.
    """
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    subject = GenericForeignKey('content_type', 'object_id')
    last_used = ModificationDateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        unique_together = ('name', 'object_id', 'content_type')


class TaggedObjectMixin(models.Model):
    """
    Tagged Mixin, supplying a relation with tags
    """

    tags = GenericRelation(Tag, content_type_field='content_type', object_id_field='object_id')

    class Meta:
        abstract = True

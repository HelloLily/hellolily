from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _

from lily.tenant.models import TenantMixin


class Tag(TenantMixin):
    """
    Tag model, simple char field to store a tag. Is used to describe the model it is linked to.
    """
    name = models.CharField(max_length=50, verbose_name=_('tag'))

    content_type = models.ForeignKey(ContentType)
    object_id  = models.PositiveIntegerField()
    subject = generic.GenericForeignKey('content_type','object_id')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        unique_together = ('name', 'object_id')


class TaggedObjectMixin(models.Model):
    """
    Tagged Mixin, supplying a relation with tags
    """
    
    tags = generic.GenericRelation(Tag, content_type_field='content_type', object_id_field='object_id', 
                                   verbose_name=_('list of tags'))
    
    class Meta:
        abstract = True
    


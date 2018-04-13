from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from lily.tenant.models import TenantMixin
from lily.socialmedia.models import SocialMedia

from .models import PhoneNumber, Address, EmailAddress


class DeletedMixin(TimeStampedModel):
    """
    Deleted model, flags when an instance is deleted.
    """
    deleted = models.DateTimeField(_('deleted'), null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, hard=False):
        """
        Soft delete instance by flagging is_deleted as True.

        Arguments:
            using (str): which db to use
            hard (boolean): If True, permanent removal from db
        """
        if hard:
            super(DeletedMixin, self).delete(using=using)
        else:
            self.is_deleted = True
            self.deleted = timezone.now()
            self.save()

    class Meta:
        abstract = True


class Common(DeletedMixin, TenantMixin):
    """
    Common model to make it possible to easily define relations to other models.
    """
    phone_numbers = models.ManyToManyField(
        to=PhoneNumber,
        blank=True,
        verbose_name=_('list of phone numbers')
    )
    social_media = models.ManyToManyField(
        to=SocialMedia,
        blank=True,
        verbose_name=_('list of social media')
    )
    addresses = models.ManyToManyField(
        to=Address,
        blank=True,
        verbose_name=_('list of addresses')
    )
    email_addresses = models.ManyToManyField(
        to=EmailAddress,
        blank=True,
        verbose_name=_('list of email addresses')
    )
    notes = GenericRelation(
        to='notes.Note',
        content_type_field='gfk_content_type',
        object_id_field='gfk_object_id',
        verbose_name=_('list of notes')
    )

    @property
    def twitter(self):
        try:
            twitter = self.social_media.filter(name='twitter').first()
        except SocialMedia.DoesNotExist:
            pass
        else:
            return twitter.username

    @property
    def linkedin(self):
        try:
            linkedin = self.social_media.filter(name='linkedin').first()
        except SocialMedia.DoesNotExist:
            pass
        else:
            return linkedin.profile_url

    class Meta:
        abstract = True


class ArchivedMixin(models.Model):
    """
    Archived model, if set to true, the instance is archived.
    """
    is_archived = models.BooleanField(default=False)

    class Meta:
        abstract = True

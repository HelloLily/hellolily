from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.models import TimeStampedModel

from lily.tenant.models import TenantMixin
from lily.utils.models import PhoneNumber, Address, EmailAddress
from lily.utils.models.fields import PhoneNumberFormSetField, AddressFormSetField, EmailAddressFormSetField
from lily.socialmedia.models import SocialMedia


class DeletedMixin(TimeStampedModel):
    """
    Deleted model, flags when an instance is deleted.
    """
    deleted = ModificationDateTimeField(_('deleted'))
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class Common(DeletedMixin, TenantMixin):
    """
    Common model to make it possible to easily define relations to other models.
    """
    phone_numbers = PhoneNumberFormSetField(PhoneNumber, blank=True, verbose_name=_('list of phone numbers'))
    social_media = models.ManyToManyField(SocialMedia, blank=True, verbose_name=_('list of social media'))
    addresses = AddressFormSetField(Address, blank=True, verbose_name=_('list of addresses'))
    email_addresses = EmailAddressFormSetField(EmailAddress, blank=True, verbose_name=_('list of e-mail addresses'))

    notes = generic.GenericRelation('notes.Note', content_type_field='content_type', object_id_field='object_id', verbose_name='list of notes')

    class Meta:
        abstract = True


class CaseClientModelMixin(object):
    """
    Contains helper function for retrieving cases based on priority or status.
    """
    def get_cases(self, priority=None, status=None):
        case_list = self.case_set.all()

        if priority:
            case_list = case_list.filter(priority=priority)

        if status:
            case_list = case_list.filter(status=status)

        return case_list


class ArchivedMixin(models.Model):
    """
    Archived model, if set to true, the instance is archived.
    """
    is_archived = models.BooleanField(default=False)

    class Meta():
        abstract = True

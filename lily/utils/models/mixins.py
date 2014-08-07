from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.models import TimeStampedModel

from lily.tenant.models import TenantMixin
from lily.utils.models import PhoneNumber, SocialMedia, Address, EmailAddress
from lily.utils.models.fields import PhoneNumberFormSetField, AddressFormSetField, EmailAddressFormSetField


class Deleted(TimeStampedModel):
    """
    Deleted model, flags when an instance is deleted.
    """
    deleted = ModificationDateTimeField(_('deleted'))
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Common(Deleted, TenantMixin):
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
    Contains helper functions for retrieving cases based on priority or status.
    """
    def get_cases(self, priority=None, status=None):
        try:
            if None not in [priority, status]:
                return self.case_set.filter(priority=priority, status=status)

            if priority is not None:
                return self.case_set.filter(priority=priority)

            if status is not None:
                return self.case_set.filter(status=status)

            return self.case_set.all()
        except:
            return self.case_set.none()

    def get_cases_critical(self):
        return self.get_cases(priority=3)

    def get_cases_high(self):
        return self.get_cases(priority=2)

    def get_cases_medium(self):
        return self.get_cases(priority=1)

    def get_cases_low(self):
        return self.get_cases(priority=0)

    def get_cases_open(self):
        return self.get_cases(status=0)

    def get_cases_progress(self):
        return self.get_cases(status=1)

    def get_cases_pending(self):
        return self.get_cases(status=2)

    def get_cases_closed(self):
        return self.get_cases(status=3)


class ArchivedMixin(models.Model):
    """
    Archived model, if set to true, the instance is archived.
    """
    is_archived = models.BooleanField(default=False)

    class Meta():
        abstract = True

from django.db import models
from django.utils import timezone
from oauth2client.contrib.django_orm import CredentialsField

from lily.contacts.models import Contact
from lily.deals.models import Deal, DealStatus, DealNextStep
from lily.tenant.models import TenantMixin


class IntegrationType(models.Model):
    name = models.CharField(max_length=255)
    auth_url = models.CharField(max_length=255)
    token_url = models.CharField(max_length=255)
    scope = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.name


class IntegrationDetails(TenantMixin):
    type = models.ForeignKey(IntegrationType, related_name='details')
    created = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return '%s credentials for %s' % (self.type.name, self.tenant)

    class Meta:
        unique_together = ('tenant', 'type')


class SlackDetails(IntegrationDetails):
    team_id = models.CharField(max_length=255)


class IntegrationCredentials(models.Model):
    details = models.OneToOneField(IntegrationDetails, primary_key=True)
    credentials = CredentialsField()


class Document(TenantMixin):
    contact = models.ForeignKey(Contact)
    deal = models.ForeignKey(Deal)
    document_id = models.CharField(max_length=255)

    EMAIL_TEMPLATE_PARAMETERS = ['sign_url']


class DocumentEvent(TenantMixin):
    event_type = models.CharField(max_length=255)
    document_status = models.CharField(max_length=255)
    status = models.ForeignKey(DealStatus, blank=True, null=True, on_delete=models.SET_NULL)
    next_step = models.ForeignKey(DealNextStep, blank=True, null=True, on_delete=models.SET_NULL)
    extra_days = models.PositiveIntegerField(blank=True, null=True)
    set_to_today = models.BooleanField(default=False)
    add_note = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tenant', 'event_type', 'document_status')

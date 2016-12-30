from django.db import models
from django.utils import timezone
from oauth2client.contrib.django_orm import CredentialsField

from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.tenant.models import TenantMixin


class IntegrationType(models.Model):
    PANDADOC, MONEYBIRD, SLACK = range(1, 4)

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


class IntegrationCredentials(models.Model):
    details = models.OneToOneField(IntegrationDetails, primary_key=True)
    credentials = CredentialsField()


class Document(TenantMixin):
    contact = models.ForeignKey(Contact)
    deal = models.ForeignKey(Deal)
    document_id = models.CharField(max_length=255)

    EMAIL_TEMPLATE_PARAMETERS = ['sign_url']

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import CredentialsField

from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.tenant.models import TenantMixin


class IntegrationDetails(TenantMixin):
    PANDADOC, SLACK = range(2)
    INTEGRATION_TYPES = (
        (PANDADOC, _('PandaDoc')),
        (SLACK, _('Slack')),
    )

    type = models.IntegerField(choices=INTEGRATION_TYPES)
    created = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return '%s credentials for %s' % (self.get_type_display(), self.tenant)

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

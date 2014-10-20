from django.db import models
from lily.tenant.models import TenantMixin


class Parcel(TenantMixin):
    DPD = range(1)
    PROVIDERS = [
        (DPD, 'DPD'),
    ]
    provider = models.IntegerField(choices=PROVIDERS, default=DPD)
    identifier = models.CharField(max_length=255)

    def get_link(self):
        if self.provider == self.DPD:
            return 'http://extranet.dpd.de/cgi-bin/delistrack?typ=1&lang=nl&pknr=%s' % self.identifier

    def __unicode__(self):
        return '%s: %s' % (self.provider, self.identifier)

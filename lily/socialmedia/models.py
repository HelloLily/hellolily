from django.db import models
from django.utils.translation import ugettext_lazy as _

from lily.tenant.models import TenantMixin


class SocialMedia(TenantMixin):
    """
    Social media model, default supporting a few well known social media but has support for
    custom input (other_name).
    """
    SOCIAL_NAME_CHOICES = (
        ('facebook', _('Facebook')),
        ('twitter', _('Twitter')),
        ('linkedin', _('LinkedIn')),
        ('googleplus', _('Google+')),
        ('qzone', _('Qzone')),
        ('orkut', _('Orkut')),
        ('other', _('Other')),
    )

    name = models.CharField(max_length=30, choices=SOCIAL_NAME_CHOICES)
    other_name = models.CharField(max_length=30, blank=True)  # used in combination with name='other'
    username = models.CharField(max_length=100, blank=True)
    profile_url = models.URLField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('social media')
        verbose_name_plural = _('social media')

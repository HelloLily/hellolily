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

    name = models.CharField(max_length=30, choices=SOCIAL_NAME_CHOICES, verbose_name=_('name'))
    other_name = models.CharField(max_length=30, blank=True, null=True)  # used in combination with name='other'
    username = models.CharField(max_length=100, blank=True, verbose_name=_('username'))
    profile_url = models.URLField(max_length=255, verbose_name=_('profile link'), blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_name(self):
        """Get the pretty name from 'name' or 'other'."""
        if self.name and self.name is not 'other':
            return dict(self.SOCIAL_NAME_CHOICES).get(self.name)
        return self.other

    class Meta:
        verbose_name = _('social media')
        verbose_name_plural = _('social media')

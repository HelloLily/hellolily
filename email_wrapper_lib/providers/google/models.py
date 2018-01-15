from django.db import models
from django.utils.translation import ugettext_lazy as _


class GoogleSyncInfo(models.Model):
    account = models.ForeignKey(
        to='email_wrapper_lib.EmailAccount',
        on_delete=models.CASCADE,
        verbose_name=_('Account'),
        related_name='google_sync_info'
    )
    history_id = models.CharField(
        verbose_name=_('History token'),
        null=True,
        max_length=255
    )
    # TODO: do we need this?
    # page_token = models.CharField(
    #     verbose_name=_('Page token'),
    #     null=True,
    #     max_length=255
    # )

    class Meta:
        app_label = 'email_wrapper_lib'

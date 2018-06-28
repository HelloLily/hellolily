import analytics
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from lily.messaging.email.models.models import EmailAccount
from lily.tenant.middleware import get_current_user


@receiver(post_save, sender=EmailAccount)
def post_save_callback(sender, instance, created, **kwargs):
    """
    Track newly added email accounts in Segment. Tracking is not added in the the front-end because it isn't possible
    to differentiate between an update or create. Negative side effect is that cancelling added new email accounts is
    still tracked.
    """
    if settings.TESTING:
        return

    if created:
        user = get_current_user()
        analytics.track(user.id, 'email-account-created', {
            'email_account_id': instance.id,
            'email_account_type': 'Google',
            'email_account_address': instance.email_address,
        })

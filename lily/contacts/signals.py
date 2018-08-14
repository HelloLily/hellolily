import analytics
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from lily.contacts.models import Contact
from lily.tenant.middleware import get_current_user


@receiver(post_save, sender=Contact)
def post_save_callback(sender, instance, created, **kwargs):
    """
    Track newly added contacts in Segment.
    """
    if settings.TESTING:
        return

    if created:
        user = get_current_user()
        if user:  # User is missing when creating test data.
            analytics.track(user.id, 'contact-created', anonymous_id='Anonymous' if user.is_anonymous() else None)

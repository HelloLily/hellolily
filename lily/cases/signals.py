import analytics
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from lily.cases.models import Case
from lily.tenant.middleware import get_current_user


@receiver(post_save, sender=Case)
def post_save_callback(sender, instance, created, **kwargs):
    """
    Track newly added cases in Segment.
    """
    if settings.TESTING:
        return

    if created:
        user = get_current_user()
        if user:  # User is missing when creating test data.
            analytics.track(
                user.id,
                'case-created', {
                    'expires': instance.expires,
                    'assigned_to_id': instance.assigned_to.id if instance.assigned_to else '',
                },
                anonymous_id='Anonymous' if user.is_anonymous() else None
            )

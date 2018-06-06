import analytics
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from lily.deals.models import Deal
from lily.tenant.middleware import get_current_user


@receiver(post_save, sender=Deal)
def post_save_callback(sender, instance, created, **kwargs):
    """
    Track newly added deals in Segment.
    """
    if settings.TESTING:
        return

    if created:
        user = get_current_user()
        if user:  # User is missing when creating test data.
            analytics.track(user.id, 'deal-created', {
                'assigned_to_id': instance.assigned_to.id,
                'status': instance.status.name,
                'next_step': instance.next_step.name,
            })

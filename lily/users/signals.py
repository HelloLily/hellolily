import analytics
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from lily.tenant.middleware import get_current_user
from lily.users.models import LilyUser, UserInvite


@receiver(user_logged_in)
def logged_in_callback(sender, user, request, **kwargs):
    """
    Identify newly logged in user in Segment.
    """
    plan_tier = None
    try:
        plan_tier = user.tenant.billing.plan.tier
    except AttributeError:
        pass

    analytics.identify(user.id, {
        'name': user.full_name,
        'email': user.email,
        'tenant_id': user.tenant.id,
        'tenant_name': user.tenant.name,
        'plan_tier': plan_tier,
        'is_free_plan': user.tenant.billing.is_free_plan,
    })


@receiver(post_save, sender=LilyUser)
def post_save_user_callback(sender, instance, created, **kwargs):
    """
    Identify created and updated users in Segment.
    """
    if settings.TESTING:
        return

    plan_tier = None
    try:
        plan_tier = instance.tenant.billing.plan.tier
    except AttributeError:
        pass

    analytics.identify(instance.id, {
        'name': instance.full_name,
        'email': instance.email,
        'tenantId': instance.tenant.id,
        'tenantName': instance.tenant.name,
        'planTier': plan_tier,
        'isFreePlan': instance.tenant.billing.is_free_plan,
    })


@receiver(post_save, sender=UserInvite)
def post_save_invite_callback(sender, instance, created, **kwargs):
    if settings.TESTING:
        return

    if created:
        user = get_current_user()
        analytics.track(user.id, 'invite-created', {
            'email': instance.email,
            'tenant_id': instance.tenant.id,
            'date': instance.date,
        })

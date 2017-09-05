from rest_framework.permissions import BasePermission

from lily.utils.functions import has_required_tier


class IsAccountAdmin(BasePermission):
    """
    Global permission check for if the user is in the account_admin group.
    """

    def has_permission(self, request, view):
        user = request.user

        return user.is_admin


class IsFeatureAvailable(BasePermission):
    def has_permission(self, request, view):
        # We'll just put the default tier at one since that's the most common requirement.
        required_tier = getattr(view, 'required_tier', 1)

        # API access isn't available for the free and cheapest paid plan.
        return not has_required_tier(required_tier)

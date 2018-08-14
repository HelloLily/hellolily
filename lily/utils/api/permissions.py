from rest_framework.permissions import BasePermission

from lily.utils.functions import has_required_tier


class IsAccountAdmin(BasePermission):
    """
    Global permission check for if the user is in the account_admin group.
    Certain endpoints might allow other users to access certain methods.
    """

    def has_permission(self, request, view):
        user = request.user

        # We might want to allow certain methods for an endpoint (e.g. GET requests).
        unrestricted_methods = getattr(view, 'unrestricted_methods', None)

        if unrestricted_methods and request.method in unrestricted_methods:
            return True

        return user.is_admin


class IsFeatureAvailable(BasePermission):
    def has_permission(self, request, view):
        # We'll just put the default tier at two since that's the most common requirement.
        required_tier = getattr(view, 'required_tier', 2)

        # API access isn't available for the free and cheapest paid plan.
        return has_required_tier(required_tier)

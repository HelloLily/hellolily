from rest_framework.permissions import BasePermission


class IsAccountAdmin(BasePermission):
    """
    Global permission check for if the user is in the account_admin group.
    """

    def has_permission(self, request, view):
        user = request.user

        return user.is_admin

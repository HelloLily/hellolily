from lily.tenant.middleware import set_current_user


class SetTenantUserMixin(object):
    """
    Mixin used to set the tenant user for this API.
    """
    def perform_authentication(self, request):
        """
        Set the tenant user for the tenant filters etc.
        """
        set_current_user(request.user)

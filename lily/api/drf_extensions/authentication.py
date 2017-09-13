from rest_framework.authentication import BaseAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import PermissionDenied

from lily.tenant.middleware import set_current_user
from lily.utils.functions import has_required_tier


class TokenGETAuthentication(TokenAuthentication):
    """
    Allows for token authentication based on the GET parameter.
    """
    def authenticate(self, request):
        token = request.GET.get('key', None)
        if not token:
            return None

        return self.authenticate_credentials(token)


class LilyApiAuthentication(BaseAuthentication):
    authenticators = (SessionAuthentication, TokenAuthentication, TokenGETAuthentication)

    def authenticate(self, request):
        for authenticator_cls in self.authenticators:
            authenticator = authenticator_cls()

            auth_tuple = authenticator.authenticate(request)
            if auth_tuple:
                if isinstance(authenticator, TokenAuthentication) or isinstance(authenticator, TokenGETAuthentication):
                    if not has_required_tier(2, tenant=auth_tuple[0].tenant):
                        raise PermissionDenied({
                            'detail': (
                                'API access has been disabled because you are on the free plan.'
                                'Please upgrade to continue using the API'
                            )
                        })
                        # Tenant is on free plan, so no external API access.
                        return None

                break
        else:
            # All authentication failed.
            return None

        # Set the current user for the tenant filters.
        set_current_user(auth_tuple[0])

        return auth_tuple

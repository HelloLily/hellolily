from rest_framework.authentication import BaseAuthentication, SessionAuthentication, TokenAuthentication

from lily.tenant.middleware import set_current_user


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
            auth_tuple = authenticator_cls().authenticate(request)
            if auth_tuple:
                break
        else:
            # All authentication failed.
            return None

        # Set the current user for the tenant filters.
        set_current_user(auth_tuple[0])

        return auth_tuple

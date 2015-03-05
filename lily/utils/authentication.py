from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class TokenGETAuthentication(TokenAuthentication):
    """
    Allows for token authentication based on the GET parameter.
    """
    def authenticate(self, request):
        token = request.GET.get('key', '')
        if not token:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        return self.authenticate_credentials(token)

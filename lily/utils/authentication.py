from rest_framework.authentication import TokenAuthentication


class TokenGETAuthentication(TokenAuthentication):
    """
    Allows for token authentication based on the GET parameter.
    """
    def authenticate(self, request):
        token = request.GET.get('key', None)
        if not token:
            return None

        return self.authenticate_credentials(token)

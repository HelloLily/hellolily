from django.conf import settings

from ..exceptions import InvalidProfileError
from .base import BaseAuthProvider


class MicrosoftAuthProvider(BaseAuthProvider):
    client_id = settings.SOCIAL_AUTH_MICROSOFT_CLIENT_ID
    client_secret = settings.SOCIAL_AUTH_MICROSOFT_SECRET
    scope = [
        'openid',
        'User.Read',
    ]
    auth_uri = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    token_uri = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    jwks_uri = 'https://login.microsoftonline.com/common/discovery/v2.0/keys'

    def parse_profile(self, session, token):
        try:
            profile = session.get('https://graph.microsoft.com/v1.0/me/').json()
        except ValueError:
            raise InvalidProfileError()

        email = profile.get('userPrincipalName', '')
        if not email:
            raise InvalidProfileError()

        picture = self.get_picture(session, 'https://graph.microsoft.com/v1.0/me/photo/$value')
        language = self.get_language(profile.get('preferredLanguage', ''))

        return {
            'email': email,
            'picture': picture,
            'first_name': profile.get('givenName', ''),
            'last_name': profile.get('surname', ''),
            'language': language
        }

from django.conf import settings

from ..exceptions import InvalidProfileError
from .base import BaseAuthProvider


class GoogleAuthProvider(BaseAuthProvider):
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    client_secret = settings.SOCIAL_AUTH_GOOGLE_SECRET
    scope = [
        'https://www.googleapis.com/auth/plus.me',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    auth_uri = 'https://accounts.google.com/o/oauth2/v2/auth'
    token_uri = 'https://www.googleapis.com/oauth2/v4/token'
    jwks_uri = 'https://www.googleapis.com/oauth2/v3/certs'

    def parse_profile(self, session, token):
        id_token = token['id_token']

        email = id_token.get('email', '')
        if not email or not id_token.get('email_verified', False):
            raise InvalidProfileError()

        picture = self.get_picture(session=session, url=id_token.get('picture', ''))
        language = self.get_language(id_token.get('locale', ''))

        return {
            'email': email,
            'picture': picture,
            'first_name': id_token.get('given_name', ''),
            'last_name': id_token.get('family_name', ''),
            'language': language,
        }

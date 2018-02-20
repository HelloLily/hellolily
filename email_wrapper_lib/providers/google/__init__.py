from email_wrapper_lib.conf import settings
from oauth2client.client import OAuth2WebServerFlow

from .connector import GoogleConnector


class Google(object):
    id = 1
    name = 'google'
    logo = 'path/to/logo'

    connector = GoogleConnector
    flow = OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        redirect_uri='{0}/{1}/'.format(settings.OAUTH2_REDIRECT_URI, name),
        scope='https://mail.google.com/',
        prompt='consent',
        access_type='offline',
    )

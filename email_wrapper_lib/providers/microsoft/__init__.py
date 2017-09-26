from oauth2client.client import OAuth2WebServerFlow

from email_wrapper_lib.conf import settings

from .connector import MicrosoftConnector


class Microsoft(object):
    id = 2
    name = 'microsoft'
    logo = 'path/to/logo'

    connector = MicrosoftConnector
    flow = OAuth2WebServerFlow(
        client_id=settings.MICROSOFT_OAUTH2_CLIENT_ID,
        client_secret=settings.MICROSOFT_OAUTH2_CLIENT_SECRET,
        redirect_uri='{0}/{1}/'.format(settings.OAUTH2_REDIRECT_URI, name),
        scope=[
            'openid',
            'offline_access',
            'https://outlook.office.com/mail.read',
            'https://outlook.office.com/mail.send',
            'https://outlook.office.com/mail.readwrite',
            'https://outlook.office.com/mailboxsettings.read',
            'https://outlook.office.com/mailboxsettings.readwrite',
        ],
        prompt='consent',
        access_type='offline',
        auth_uri='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        token_uri='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        token_info_uri='https://login.microsoftonline.com/common/oauth2/v2.0/tokeninfo'
    )

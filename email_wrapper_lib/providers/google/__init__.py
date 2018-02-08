from email_wrapper_lib.conf import settings
from oauth2client.client import OAuth2WebServerFlow

from email_wrapper_lib.models import EmailAccount

# Register all the stuff google provider uses.
from .connector import GoogleConnector
from .manager import GoogleManager
from .models import GoogleSyncInfo
from .tasks import stop_syncing, save_folders, save_page, debug_task, raising_task


class Google(object):
    id = EmailAccount.GOOGLE
    name = 'google'
    logo = 'path/to/logo'

    manager = GoogleManager
    connector = GoogleConnector

    flow = OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        redirect_uri='{0}/{1}/'.format(settings.OAUTH2_REDIRECT_URI, name),
        scope='https://mail.google.com/',
        prompt='consent',
        access_type='offline',
    )

import logging
from oauth2client.contrib.django_orm import Storage

from .models.models import GmailCredentialsModel
from .exceptions import InvalidCredentialsError


logger = logging.getLogger(__name__)


def get_credentials(gmail_account):
    """
    Get the credentials for the given EmailAccount, what should be a Gmail account.

    If there are no valid credentials for the account, is_authorized is set to
    False and there will be an InvalidCredentialsError raised.

    Arguments:
        gmail_account (instance): EmailAccount instance

    Returns:
        credentials for the EmailAccount

    Raises:
        InvalidCredentialsError, if there are no valid credentials for the account.

    """
    storage = Storage(GmailCredentialsModel, 'id', gmail_account, 'credentials')
    credentials = storage.get()

    if credentials is not None and credentials.invalid is False:
        return credentials
    else:
        gmail_account.is_authorized = False
        gmail_account.save()
        logger.error('No or invalid credentials for account %s' % gmail_account)
        raise InvalidCredentialsError('No or invalid credentials for account %s' % gmail_account)

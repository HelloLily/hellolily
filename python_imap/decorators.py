from functools import wraps
from imaplib import IMAP4

from python_imap.errors import IMAPConnectionError
from python_imap.logger import logger


def logout_on_failure(func):
    """
    Decorator to catch IMAP4 errors.

    When it happens, it attempts to log out the client.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except IMAP4.error, e:
            logger.warn(e)
            try:
                self.client.logout()
            except:  # pylint: disable=W0702
                pass  # ignore more exceptions: `e` is logged already

            raise IMAPConnectionError(str(e))
    return wrapper

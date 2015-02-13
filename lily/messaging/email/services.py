import httplib2

from googleapiclient.discovery import build


def build_gmail_service(credentials):
    """
    Build a Gmail service object.

    Args:
      credentials (instance): OAuth 2.0 credentials.

    Returns:
      Gmail service object.
    """
    http = credentials.authorize(httplib2.Http())
    return build('gmail', 'v1', http=http)

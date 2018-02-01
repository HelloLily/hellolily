from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import HttpAccessTokenRefreshError

from email_wrapper_lib.providers.exceptions import BatchRequestException


def new_batch(service):
    service = build('gmail', 'v1')
    return service.new_batch_http_request()


def execute_batch(batch):
    try:
        batch.execute()
    except BatchRequestException:
        pass
    except HttpAccessTokenRefreshError:
        pass
    except HttpError:
        pass


def execute_request(request):
    try:
        data = request.execute()
    except HttpAccessTokenRefreshError:
        pass
    except HttpError:
        pass

    return data

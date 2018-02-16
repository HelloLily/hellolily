import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import HttpAccessTokenRefreshError

from email_wrapper_lib.providers.exceptions import BatchRequestException


# TODO: figure out if these functions are actually handy..


def new_service(credentials=None):
    # TODO: use the predefined json file from data to save us a request.
    if credentials:
        http = credentials.authorize(httplib2.Http())
    else:
        http = httplib2.Http()

    return build('gmail', 'v1', http=http)


def new_batch():
    service = new_service()
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
    data = None
    try:
        data = request.execute()
    except HttpAccessTokenRefreshError:
        pass
    except HttpError:
        pass

    return data

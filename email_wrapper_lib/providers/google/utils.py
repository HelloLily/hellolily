import httplib2
from googleapiclient.discovery import build


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

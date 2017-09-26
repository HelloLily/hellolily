import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import HttpAccessTokenRefreshError

from email_wrapper_lib.providers.exceptions import BatchRequestException
from .resources import (
    GoogleHistoryResource, GoogleLabelsResource, GoogleMessagesResource, GoogleProfileResource
)


def build_service(credentials=None):
    if credentials:
        http = credentials.authorize(httplib2.Http())
    else:
        http = httplib2.Http()

    return build('gmail', 'v1', http=http)


class BatchStore(object):
    __instance = None
    batch = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

            cls.service = build_service()  # TODO: missing user_id & credentials, should be provided?
            cls.__instance.batch = cls.service.new_batch_http_request()

        return cls.__instance

    def reset(self):
        batch = self.service.new_batch_http_request()
        self.batch = batch
        return batch


class GoogleConnector(object):
    def __init__(self, user_id, credentials):
        self.service = build_service(user_id, credentials)
        self.user_id = user_id
        self.batch = BatchStore().batch

    @property
    def profile(self):
        return GoogleProfileResource(self.service, self.user_id, self.batch)

    @property
    def messages(self):
        return GoogleMessagesResource(self.service, self.user_id, self.batch)

    @property
    def labels(self):
        return GoogleLabelsResource(self.service, self.user_id, self.batch)

    @property
    def history(self):
        return GoogleHistoryResource(self.service, self.user_id, self.batch)

    def execute(self):
        try:
            self.batch.execute()
        except BatchRequestException:
            pass
        except HttpAccessTokenRefreshError:
            pass
        except HttpError:
            pass
        finally:
            self.batch = BatchStore().reset()

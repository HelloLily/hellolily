from microsoft_mail_client.errors import HttpError
from microsoft_mail_client.service import build
from .resources import (
    MicrosoftProfileResource, MicrosoftMessagesResource, MicrosoftLabelsResource, MicrosoftHistoryResource
)


def build_service(user_id, credentials=None):
    """
    :param user_id: 'me' or an email address.
    :param credentials:
    :return: api service object.
    """
    # if credentials:
    #     http = credentials.authorize(httplib2.Http())
    # else:
    #     http = httplib2.Http()

    return build('v2.0', user_id, credentials)


class BatchStore(object):
    # TODO: Move to util class, reused with Google connector.

    __instance = None  # TODO: explain, reset() doesn't touch __instance.
    batch = None

    def __new__(cls, user_id, credentials):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

            cls.service = build_service(user_id, credentials)
            cls.__instance.batch = cls.service.new_batch_http_request()

        return cls.__instance

    def reset(self):
        batch = self.service.new_batch_http_request()
        self.batch = batch
        return batch


class MicrosoftConnector(object):

    # TODO: create a decorator to enforce valid credentials for the profile, messages, labels, history and search.

    # def __init__(self, credentials, user_id):
    #     # Build a gmail service using an authorized http instance.
    #     self.http = credentials.authorize(httplib2.Http())
    #     # self.service = build('microsoft', 'v1', http=self.http)

    def __init__(self, user_id, credentials):
        self.user_id = user_id
        self.credentials = credentials
        self.service = build_service(user_id, credentials)
        self.batch = BatchStore(user_id, credentials).batch

    @property
    def profile(self):
        return MicrosoftProfileResource(self.service, self.user_id, self.batch)

    @property
    def messages(self):
        return MicrosoftMessagesResource(self.service, self.user_id, self.batch)

    @property
    def labels(self):
        return MicrosoftLabelsResource(self.service, self.user_id, self.batch)

    @property
    def history(self):
        return MicrosoftHistoryResource(self.service, self.user_id, self.batch)

    def execute(self):
        try:
            print "Execute batch"
            print self.batch
            self.batch.execute()
        # except BatchRequestException:
        #     pass
        # except HttpAccessTokenRefreshError:
        #     pass
        except HttpError as e:  # TODO: Right error?
            print e
        finally:
            print "Reset"
            self.batch = BatchStore(self.user_id, self.credentials).reset()

import httplib2

from .resources import (
    MicrosoftProfileResource, MicrosoftMessagesResource, MicrosoftLabelsResource, MicrosoftHistoryResource
)


class MicrosoftConnector(object):
    # Connector should not do anything with the db, that is the managers job.
    # Connector should just transform the received json into an internal format.

    # TODO: create a decorator to enforce valid credentials for the profile, messages, labels, history and search.

    def __init__(self, credentials):
        # Build a gmail service using an authorized http instance.
        self.http = credentials.authorize(httplib2.Http())
        # self.service = build('microsoft', 'v1', http=self.http)

    @property
    def profile(self):
        return MicrosoftProfileResource()

    @property
    def messages(self):
        return MicrosoftMessagesResource()

    @property
    def labels(self):
        return MicrosoftLabelsResource()

    @property
    def history(self):
        return MicrosoftHistoryResource()

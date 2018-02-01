from googleapiclient.discovery import build

from .resources.folders import FoldersResource
from .resources.history import HistoryResource
from .resources.messages import MessagesResource
from .resources.profile import ProfileResource


class GoogleConnector(object):
    def __init__(self, credentials, user_id='me'):
        service = build('gmail', 'v1', credentials=credentials)

        self.profile = ProfileResource(service, user_id)
        self.messages = MessagesResource(service, user_id)
        self.folders = FoldersResource(service, user_id)
        self.history = HistoryResource(service, user_id)



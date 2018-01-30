from googleapiclient.discovery import build
from .resources import (
    GoogleHistoryResource, GoogleFolderResource, GoogleMessageResource, GoogleProfileResource
)


class GoogleConnector(object):
    def __init__(self, user_id, credentials):
        self.service = build('gmail', 'v1', credentials=credentials)
        self.user_id = user_id

        self.profile = GoogleProfileResource(self.service, self.user_id)
        self.messages = GoogleMessageResource(self.service, self.user_id)
        self.folders = GoogleFolderResource(self.service, self.user_id)
        self.history = GoogleHistoryResource(self.service, self.user_id)



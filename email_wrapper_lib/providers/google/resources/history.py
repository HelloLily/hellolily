from email_wrapper_lib.conf import settings
from email_wrapper_lib.providers.google.parsers.history import parse_history

from .base import GoogleResource


class HistoryResource(GoogleResource):
    def list(self, history_token, page_token, batch=None):
        """
        Return the history list from the api.
        """

        request = self.service.users().history().list(
            userId=self.user_id,
            quotaUser=self.user_id,
            maxResults=settings.BATCH_SIZE,
            startHistoryId=history_token,
            pageToken=page_token
        )

        return self.execute(request, parse_history, batch)

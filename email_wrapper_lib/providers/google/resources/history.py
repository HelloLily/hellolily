from email_wrapper_lib.providers.google.parsers import parse_batch_response, parse_history

from .base import GoogleResource
from .messages import GoogleMessageResource


class GoogleHistoryResource(GoogleResource):
    def list(self, history_token, page_token):
        history = {}

        # Because google only gives message ids, we need to do a second batch for the bodies.
        second_batch = self.service.new_batch_http_request()
        message_resource = GoogleMessageResource(self.service, self.user_id, second_batch)

        self.batch.add(
            self.service.users().history().list(
                userId=self.user_id,
                startHistoryId=history_token,
                pageToken=page_token
            ),
            callback=parse_batch_response(parse_history, history, message_resource)
        )

        return history

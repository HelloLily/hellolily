from email_wrapper_lib.providers.google.parsers import parse_response, parse_message_list, parse_message

from .base import GoogleResource


class GoogleMessagesResource(GoogleResource):
    def get(self, remote_id):
        message = {}

        self.batch.add(
            self.service.users().messages().get(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_response(parse_message, message)
        )

        return message

    def list(self, page_token=None):
        messages = {}

        # Because google only gives message ids, we need to do a second batch for the bodies.
        second_batch = self.service.new_batch_http_request()
        message_resource = GoogleMessagesResource(self.service, self.user_id, second_batch)

        self.batch.add(
            self.service.users().messages().list(
                userId=self.user_id,
                pageToken=page_token
            ),
            callback=parse_response(parse_message_list, messages, message_resource)
        )

        return messages

    def send(self):
        pass

    def search(self):
        pass

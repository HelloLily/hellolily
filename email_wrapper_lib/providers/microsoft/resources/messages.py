from email_wrapper_lib.providers.microsoft.parsers import parse_response, parse_message
from email_wrapper_lib.providers.microsoft.resources.base import MicrosoftResource


class MicrosoftMessagesResource(MicrosoftResource):
    def get(self, remote_id):
        message = {}

        self.batch.add(
            self.service.get_message(
                message_id=remote_id
            ),
            callback=parse_response(parse_message, message)
        )

        return message

    def list(self):
        pass

    def save_create_update(self):
        pass

    def search(self):
        pass

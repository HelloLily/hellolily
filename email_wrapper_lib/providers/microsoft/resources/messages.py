from email_wrapper_lib.providers.microsoft.parsers import parse_response, parse_message, parse_message_list
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

    def list(self, page_token=0):
        """
        Get one page of messages for the entire mailbox.
        """
        messages = {}
        query_parameters = {
            '$top': 50,  # TODO: Determine maximum. for $search it is 250, maybe here also?
            '$skip': page_token,
        }  # Paging.
        # TODO: Only request usefull data?
        # query_parameters.update({'$select': 'Id,InternetMessageId,ConversationId,BodyPreview,IsRead,IsDraft,ParentFolderId,Importance,From,ToRecipients,CcRecipients,BccRecipients,ReplyTo,Sender'})

        self.batch.add(
            self.service.get_messages(
                query_parameters=query_parameters
            ),
            callback=parse_response(parse_message_list, messages)
        )

        return messages

    def save_create_update(self):
        pass

    def search(self):
        pass

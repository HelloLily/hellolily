from email_wrapper_lib.providers.microsoft.parsers import parse_response, parse_history


class MicrosoftHistoryResource(object):
    def list(self, history_token, page_token, folder_id):
        history = {}

        query_parameters = {
        #     '$select': 'Id, InternetMessageId, ConversationId, BodyPreview, IsRead, IsDraft, ParentFolderId,'
        #                'Importance, From, ToRecipients, CcRecipients, BccRecipients, ReplyTo, Sender, HasAttachments',
            '$expand': 'Attachments',  # TODO: Or remove because HasAttachments is just enough?
        }

        self.batch.add(
            self.service.synchronize_messages(
                folder_id=folder_id,
                delta_token=history_token,
                skip_token=page_token,
            ),
            callback=parse_response(parse_history, history)
        )

        return history

    def save_create_update(self):
        pass
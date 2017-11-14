from email_wrapper_lib.providers.microsoft.parsers import (
    parse_response, parse_message, parse_message_list, parse_message_send,
    parse_deletion)
from email_wrapper_lib.providers.microsoft.resources.base import MicrosoftResource
from microsoft_mail_client.constants import (
    FOLDER_DELETED_ITEMS_ID, FOLDER_INBOX_ID, FOLDER_JUNK_ID,
    FOLDER_ARCHIVE_ID, IMPORTANCE_HIGH, IMPORTANCE_NORMAL)


class MicrosoftMessagesResource(MicrosoftResource):
    def get(self, remote_id):
        message = {}

        query_parameters = {
            # '$select': 'Id, InternetMessageId, ConversationId, BodyPreview, IsRead, IsDraft, ParentFolderId,'
            #            'Importance, From, ToRecipients, CcRecipients, BccRecipients, ReplyTo, Sender, HasAttachments',
            '$expand': 'Attachments',
        }

        self.batch.add(
            self.service.get_message(
                message_id=remote_id,
                query_parameters=query_parameters
            ),
            callback=parse_response(parse_message, message)
        )

        return message

    def list(self, page_token=0):
        """
        Get one page of messages for the entire mailbox.
        """
        if not page_token:
            page_token = 0

        messages = {}
        query_parameters = {
            '$top': 50,  # TODO: Determine maximum. for $search it is 250, maybe here also?
            '$skip': page_token,
            '$expand': 'Attachments',  # TODO: Or remove because HasAttachments is just enough?
        }  # Paging.

        # TODO: Only request usefull data?
        # query_parameters = {
        #     '$top': 50,  # TODO: Determine maximum. for $search it is 250, maybe here also?
        #     '$skip': page_token,
        #     '$select': 'Id, InternetMessageId, ConversationId, BodyPreview, IsRead, IsDraft, ParentFolderId,'
        #                'Importance, From, ToRecipients, CcRecipients, BccRecipients, ReplyTo, Sender, HasAttachments',
        #     '$expand': 'Attachments',
        # }

        self.batch.add(
            self.service.get_messages(
                query_parameters=query_parameters
            ),
            callback=parse_response(parse_message_list, messages)
        )

        return messages

    def send(self, draft):
        from email_wrapper_lib.models.models import EmailDraftToEmailRecipient  # TODO: fix import.

        # TODO: can we disregard the /forward end-point by just using /sendmail?
        # TODO: can we disregard the /replyall end-point by just using /reply?
        # In other words, by using sent_reply_message, sent_reply_all_message & sent_forward_message instead of
        # send_message we miss the possiblity to update other writable properties of a message, eg. CC, BCC,
        # attachments.

        # Draft message can be a new, a reply / reply all or a forward / forward all - message.
        status_code = None
        outgoing_message = {
            'Message': {
                'Subject': self._get_subject(draft),
                'Body': self._get_body(draft),
                'ToRecipients': self._get_recipients(EmailDraftToEmailRecipient.TO, draft.id),
                # 'CcRecipients': self._get_recipients(EmailDraftToEmailRecipient.CC, draft.id),  # TODO: Empty list allowed?
                # 'BccRecipients': self._get_recipients(EmailDraftToEmailRecipient.BCC, draft.id)  # TODO: Empty list allowed?
            }
        }

        recipient_list = self._get_recipients(EmailDraftToEmailRecipient.CC, draft.id)
        if recipient_list:
            outgoing_message['Message']['CcRecipients'] = recipient_list
        recipient_list = self._get_recipients(EmailDraftToEmailRecipient.BCC, draft.id)
        if recipient_list:
            outgoing_message['Message']['BccRecipients'] = recipient_list
        attachment_list = self._get_attachments(draft.id)
        if attachment_list:
            outgoing_message['Message']['Attachments'] = attachment_list
        # TODO: Add template attachments.
        # TODO: Add attachment from original message (if mail is being forwarded). Or are they present in EmailDraftAttachment already?
        if draft.in_reply_to:
            # Non-writable property according to the API documents. Accepted by API. But not seeing any difference
            # in Outlook webapp, Gmail & source view.
            outgoing_message['Message']['ConversationId'] = draft.in_reply_to.thread_id

        # TODO: Impossible to set Message-ID, References & In-Reply-To headers on a reply / forward. Only possible
        # by draft_reply_message / draft_forward_message.

        service_call = self.service.send_message(message=outgoing_message)

        # else:
        #     # TODO: by using sent_reply_message, sent_reply_all_message & sent_forward_message instead of send_message
        #     # we miss the possiblity to update other writable properties of a message, eg. CC, BCC, attachments.
        #     message['Comment'] = draft.body_text
        #
        #     if draft.message_type == EmailDraft.REPLY:
        #         service_call = self.service.sent_reply_message(
        #             message_id=draft.in_reply_to.message_id,
        #             message=message
        #         )
        #     elif draft.message_type == EmailDraft.REPLY_ALL:
        #         service_call = self.service.sent_reply_all_message(
        #             message_id=draft.in_reply_to.message_id,
        #             message=message
        #         )
        #     else:
        #         # draft.message_type == EmailDraft.FORWARD
        #         service_call = self.service.sent_forward_message(
        #             message_id=draft.in_reply_to.message_id,
        #             message=message
        #         )

        self.batch.add(
            service_call,
            callback=parse_response(parse_message_send, status_code)
        )

        return status_code

    def search(self):
        pass

    def move(self, remote_id, remote_label_id):
        message = {}

        self.batch.add(
            self.service.move_message(
                message_id=remote_id,
                destination_folder_id=remote_label_id
            ),
            callback=parse_response(parse_message, message)
        )

        return message

    def trash(self, remote_id):
        return self.move(remote_id, FOLDER_DELETED_ITEMS_ID)

    def untrash(self, remote_id):
        return self.move(remote_id, FOLDER_INBOX_ID)  # TODO: Ok to move back to Inbox? Possible different behaviour with Google.

    def delete(self, remote_id):
        status_code = None

        self.batch.add(
            self.service.delete_message(
                message_id=remote_id,
            ),
            callback=parse_response(parse_deletion, status_code)
        )

        return status_code

    def spam(self, remote_id):
        return self.move(remote_id, FOLDER_JUNK_ID)

    def unspam(self, remote_id):
        return self.move(remote_id, FOLDER_INBOX_ID)  # TODO: Ok to move back to Inbox? Possible different behaviour with Google.

    def archive(self, remote_id):
        return self.move(remote_id, FOLDER_ARCHIVE_ID)

    def unarchive(self, remote_id):
        return self.move(remote_id, FOLDER_INBOX_ID)  # TODO: Ok to move back to Inbox? Possible different behaviour with Google.

    def read(self, remote_id):
        return self._set_message_property(remote_id, {'IsRead': True})

    def unread(self, remote_id):
        return self._set_message_property(remote_id, {'IsRead': False})

    def important(self, remote_id):
        return self._set_message_property(remote_id, {'Importance': IMPORTANCE_HIGH})

    def unimportant(self, remote_id):
        return self._set_message_property(remote_id, {'Importance': IMPORTANCE_NORMAL})

    def _get_body(self, draft):
        if draft.body_html:
            return {
                'ContentType': 'HTML',
                'Content': draft.body_html  # TODO: Or does the draft.body_html already holds reply / forward contstruction?
            }
        else:
            return {
                'ContentType': 'Text',
                'Content': draft.body_text  # TODO: Or does the draft.body_text already holds reply / forward contstruction?
            }

    def _get_subject(self, draft):
        from email_wrapper_lib.models.models import EmailDraft  # TODO: fix import.

        subject = draft.subject  # TODO: Or does the draft.subject already holds the 'Re: ' & 'Fwd: ' parts?
        if draft.message_type == EmailDraft.REPLY or draft.message_type == EmailDraft.REPLY_ALL:
            subject = "Re: {0}".format(subject)
        elif draft.message_type == EmailDraft.FORWARD or draft.message_type == EmailDraft.FORWARD_ALL:
            subject = "Fwd: {0}".format(subject)

        return subject

    def _get_recipients(self, recipient_type, draft_id):
        from email_wrapper_lib.models.models import EmailDraftToEmailRecipient  # TODO: fix import.
        recipients_list = []
        recipients = EmailDraftToEmailRecipient.objects.filter(
            draft=draft_id,
            recipient_type=recipient_type
        ).values_list('name', 'email_address')
        for recipient in recipients:
            recipients_list.append({
                'EmailAddress': {
                    'Address': recipient.email_address,
                    'Name': recipient.name
                }
            })

        return recipients_list

    def _get_attachments(self, draft_id):
        # attachment_file = 'SUQsbmFtZSxlbWFpbCBhZGRyZXNzLHBob25lIG51bWJlcix3ZWJzaXRlLHR3aXR0ZXIsYWRkcmVzcyxwb3N0Y' \
        #                   'WwgY29kZSxjaXR5CjE2LEJWIEksaW5mb0BidjEuY29tLCszMSgyMCk1NTExMjIzLGh0dHA6Ly93d3cuYnYxLm' \
        #                   'NvbSxidjEsLCwKMTcsQlYgSUksaW5mb0BidjIuY29tLDA2MjU1NTIxMTQ4LGJ2Mi5jb20sYnYyLFN0cmFhdCA' \
        #                   '0LCwKMTgsQlYgSUlJLGluZm9AYnYzLmNvbSwwMjA1NTExMjIzLHd3dy5idjMuY29tLGJ2MywsNzc1NUFBLAox' \
        #                   'OSxCViBJVixpbmZvQGJ2NC5jb20sKzMxNjU1MTEyMjMsYnY0LmNvbSxidjQsLCxBbXN0ZXJkYW0KMjAsQlYgV' \
        #                   'ixpbmZvQGJ2NS5jb20sKzMxKDIwKTU1MTEyMjMsLGJ2NSxTdHJhYXQgNCw3NzU1QUEsQW1zdGVyZGFtCjIxLE' \
        #                   'JWIElJSSxpbmZvQGJ2My5jb20sMDIwNTUxMTIyMyx3d3cuYnYzLmNvbSxidjMsLDc3NTVBQSwK'
        # return [{
        #     '@odata.type': '#Microsoft.OutlookServices.FileAttachment',
        #     'Name': 'upload.csv',
        #     'ContentBytes': attachment_file
        # }]
        from email_wrapper_lib.models.models import EmailDraftAttachment  # TODO: fix import.
        # TODO: How to handle inline attachments?
        attachment_list = []
        attachments = EmailDraftAttachment.objects.filter(draft=draft_id)
        for attachment in attachments:
            attachment_list.append({
                '@odata.type': '#Microsoft.OutlookServices.FileAttachment',
                'Name': attachment.file.name,
                'ContentBytes': attachment.file  # TODO Probably still needs to be converted to base64.
            })

        return attachment_list

    def _set_message_property(self, remote_id, properties):
        message = {}

        self.batch.add(
            self.service.update_message(
                message_id=remote_id,
                properties=properties,
            ),
            callback=parse_response(parse_message, message)
        )

        return message

from StringIO import StringIO
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from email_wrapper_lib.providers.exceptions import IllegalLabelException
from email_wrapper_lib.providers.google.parsers import (
    parse_batch_response, parse_message_list, parse_message, parse_deletion
)
from lily.settings import settings

from .base import GoogleResource


default_page_size = 100


class MessageParser(object):
    pass


class Promise(object):
    """
    A promise used for batched requests.
    """
    # TODO: use a proper promise/future lib.
    pass


class MessagesResource(object):
    def __init__(self, service, user_id):
        if user_id == 'me':
            raise ValueError('user_id must not be `me` but an actual value.')

        self.service = service
        self.user_id = user_id

    def execute(self, request, parser, batch=None):
        if batch:
            promise = Promise()

            batch.add(
                request,
                callback=parse_batch_response(parser, promise)
            )

            return promise
        else:
            # No batch object was given so we execute in place.
            try:
                response = request.execute()
                return parser(response)
            except HttpError as error:
                # TODO: error handling.
                pass

    def get(self, msg_id, batch=None):
        """
        Return a single message from the api.
        """
        request = self.service.users().messages().get(
            userId=self.user_id,
            quotaUser=self.user_id,
            id=msg_id
        )

        return self.execute(request, parse_message, batch)

    def list(self, page_token=None, batch=None, q=None, page_size=default_page_size):
        """
        Return a list of messages from the api.

        Because the normal list for gmail only returns message ids, we also get the messages afterwards.
        """
        # TODO: simplify because we know we only get ids back so no need to do fancy stuff in the callback.
        request = self.service.users().messages().list(
            userId=self.user_id,
            quotaUser=self.user_id,
            maxResults=page_size,
            pageToken=page_token,
            q=q
        )

        self.execute(request, parse_message_list, batch)

    def pages(self, page_size=default_page_size):
        """
        Return a list of all page tokens.
        """
        page_token_list = [None, ]  # Add None as first page token, because the first page doesn't have one.
        has_next_page = True  # Assume we have multiple pages untill proven otherwise.
        next_page_token = None  # Start off with None as the first page token.

        while has_next_page:
            request = self.service.users().messages().list(
                userId=self.user_id,
                quotaUser=self.user_id,
                maxResults=page_size,
                pageToken=next_page_token,
                fields=['nextPageToken', ]
            )
            response = self.execute(request, parse_page)
            next_page_token = response.get('nextPageToken', None)

            if next_page_token:
                page_token_list.append(next_page_token)
            else:
                has_next_page = False

        return page_token_list

    def send(self):
        """
        Send a message or draft.
        """
        pass

    def delete(self, msg_id):
        """
        Hard delete a message, this skips the trash folder and is unrecoverable.
        """
        pass

    def modify(self, msg_id, folders_add, folders_remove):
        """
        Add and/or remove folders from a message.
        """
        pass

    def move(self, msg_id, target):
        # TODO: keep this as seperate functions?

        mapping = {
            'trash': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'untrash': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'read': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'unread': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'spam': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'unspam': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'archive': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'unarchive': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'important': {
                'addLabelIds': [],
                'removeLabelIds': [],
            },
            'unimportant': {
                'addLabelIds': [],
                'removeLabelIds': [],
            }
        }
        pass










class GoogleMessageResource(GoogleResource):
    def get(self, remote_id):
        message = {}

        self.batch.add(
            self.service.users().messages().get(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_batch_response(parse_message, message)
        )

        return message

    def list(self, page_token=None):
        messages = {}

        # Because google only gives message ids, we need to do a second batch for the bodies.
        second_batch = self.service.new_batch_http_request()
        message_resource = GoogleMessageResource(self.service, self.user_id, second_batch)

        self.batch.add(
            self.service.users().messages().list(
                userId=self.user_id,
                pageToken=page_token
            ),
            callback=parse_batch_response(parse_message_list, messages, message_resource)
        )

        return messages

    def send(self, draft):
        message = {}
        outgoing_message = {}

        # TODO: Add template attachments.
        # TODO: Add attachment from original message (if mail is being forwarded). Or are they present in EmailDraftAttachment already?

        if draft.in_reply_to:
            outgoing_message['threadId'] = draft.in_reply_to.thread_id

        message_string = self._get_message_string(draft)

        fd = StringIO(message_string)
        media = MediaIoBaseUpload(
            fd,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=settings.GMAIL_UPLOAD_RESUMABLE
        )

        self.batch.add(
            self.service.users().messages().send(
                userId=self.user_id,
                body=outgoing_message,
                media_body=media,
            ),
            callback=parse_batch_response(parse_message, message)
        )

        return message

    def search(self):
        pass

    def trash(self, remote_id):
        message = {}

        self.batch.add(
            self.service.users().messages().trash(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_batch_response(parse_message, message)
        )

        return message

    def delete(self, remote_id):
        status_code = None

        self.batch.add(
            self.service.users().messages().delete(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_batch_response(parse_deletion, status_code)
        )

        return status_code

    def untrash(self, remote_id):
        message = {}

        self.batch.add(
            self.service.users().messages().untrash(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_batch_response(parse_message, message)
        )

        return message

    def folder(self, remote_id, folders_add, folders_remove):
        """
        Update folders for email message.

        :param remote_id: id of the email message.
        :param folders_add: folders to be added.
        :param folders_remove: folders to be removed.

        :return: updated email message.
        """
        # TODO: Compare with add_and_remove_labels_for_message, why should we check if folders are actually present or not, just apply?

        if set(settings.GMAIL_LABELS_DONT_MANIPULATE) & set(folders_add) or set(
                settings.GMAIL_LABELS_DONT_MANIPULATE) & set(folders_remove):
            raise IllegalLabelException

        message = {}

        folders = {
            "addLabelIds": folders_add,
            "removeLabelIds": folders_remove
        }

        self.batch.add(
            self.service.users().messages().modify(
                userId=self.user_id,
                id=remote_id,
                body=folders
            ),
            callback=parse_batch_response(parse_message, message)
        )

        return message

    def spam(self, remote_id):
        # TODO: Compare toggle_spam_email_message, why remove all other labels? Gmail doesn't do that either.
        return self.folder(remote_id, [settings.GMAIL_LABEL_SPAM], [])

    def unspam(self, remote_id):
        return self.folder(remote_id, [], [settings.GMAIL_LABEL_SPAM])

    def archive(self, remote_id):
        # TODO: Compare with current Lily, archive removes also current label.
        return self.folder(remote_id, [], [settings.GMAIL_LABEL_INBOX])

    def unarchive(self, remote_id):
        return self.folder(remote_id, [settings.GMAIL_LABEL_INBOX], [])

    def read(self, remote_id):
        return self.folder(remote_id, [], [settings.GMAIL_LABEL_UNREAD])

    def unread(self, remote_id):
        return self.folder(remote_id, [settings.GMAIL_LABEL_UNREAD], [])

    def important(self, remote_id):
        return self.folder(remote_id, [settings.GMAIL_LABEL_IMPORTANT], [])

    def unimportant(self, remote_id):
        return self.folder(remote_id, [], [settings.GMAIL_LABEL_IMPORTANT])

    def _get_message_string(self, draft):
        """
        :type  draft: EmailDraft
        :param draft:
        """
        # from email_wrapper_lib.models.models import EmailDraftToEmailRecipient, EmailDraftAttachment  # TODO: fix import.
        # #TODO: Email template attachments?
        #
        # email_message = SafeMIMEMultipart('related')
        # email_message['Subject'] = draft.subject
        # email_message['From'] = '"{0}" <{1}>'.format(draft.account.username, draft.account.user_id)  # TODO: Compare with current implementation.
        #
        # email_message['To'] = self._get_recipients(EmailDraftToEmailRecipient.TO, draft.id)
        # cc_recipients_list = self._get_recipients(EmailDraftToEmailRecipient.CC, draft.id)
        # if cc_recipients_list:
        #     email_message['cc'] = cc_recipients_list
        # bcc_recipients_list = self._get_recipients(EmailDraftToEmailRecipient.BCC, draft.id)
        # if bcc_recipients_list:
        #     email_message['cc'] = bcc_recipients_list
        #
        # attachments = EmailDraftAttachment.objects.filter(draft_id=draft.pk)
        # # attachments = EmailDraftAttachment.objects.filter(draft_id=draft.pk, inline=True)  # TODO: possble?
        # html, text, inline_headers = replace_cid_and_change_headers(draft.body_html, attachments)
        #
        # email_message_alternative = SafeMIMEMultipart('alternative')
        # email_message.attach(email_message_alternative)
        #
        # email_message_text = SafeMIMEText(text, 'plain', 'utf-8')
        # email_message_alternative.attach(email_message_text)
        #
        # email_message_html = SafeMIMEText(html, 'html', 'utf-8')
        # email_message_alternative.attach(email_message_html)
        #
        # # Add the inline attachments to the email message.
        # for header in inline_headers:
        #     mime_message = get_mime_message_inline(header)
        #     if mime_message:
        #         email_message.attach(mime_message)
        #
        # # Add the none-inline attachments to the email message.
        # attachments = EmailDraftAttachment.objects.filter(draft_id=draft.pk, inline=False)
        # for attachment in attachments:
        #     mime_message = get_mime_message_attachment(attachment)
        #     email_message.attach(mime_message)
        #
        # return email_message
        return None

    def _get_recipients(self, recipient_type, draft_id):
        # from email_wrapper_lib.models.models import EmailDraftToEmailRecipient  # TODO: fix import.
        # recipients = EmailDraftToEmailRecipient.objects.filter(
        #     draft=draft_id,
        #     recipient_type=recipient_type
        # ).values_list('name', 'email_address')
        #
        # recipients_list = ['"{0}" <{1}>'.format(recipient[0], recipient[1]) for recipient in recipients]
        #
        # return ", ".join(recipients_list)
        return None

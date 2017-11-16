import mimetypes
from StringIO import StringIO
from email import Encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from urllib import unquote

import html2text
import os
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage
from django.core.mail import SafeMIMEMultipart, SafeMIMEText
from googleapiclient.http import MediaIoBaseUpload

from email_wrapper_lib.providers.exceptions import IllegalLabelException
from email_wrapper_lib.providers.google.parsers import (
    parse_response, parse_message_list, parse_message, parse_deletion
)
from lily.settings import settings

from .base import GoogleResource


# TODO: move to utils.
def get_attachment_filename_from_url(url):
    return unquote(url).split('/')[-1]


# TODO: move to utils.
def create_a_beautiful_soup_object(html):
    """
    Use different HTML parsers to create a BeautifulSoup object that has no empty body.

    Args:
        html (string): HTML string of the email body to be sent.

    Returns:
        soup (BeautifulSoup object or None)
    """
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')

    if soup.get_text() == '':
        soup = BeautifulSoup(html, 'html.parser')

        if soup.get_text() == '':
            soup = BeautifulSoup(html, 'html5lib')

            if soup.get_text() == '':
                soup = BeautifulSoup(html, 'xml')

                if soup.get_text == '':
                    soup = None

    return soup


# TODO: move to utils.
def replace_cid_and_change_headers(html, attachments):
    """
    Check in the html source if there is an image tag with the attribute cid (Content-Id). Loop through the attachemnts
    that are linked with the draft. If there is a match replace the source of the image with the cid information.
    Afterwards read the image information from disk and put the data in a header.
    At last create a plain text version of the html email.

    Args:
        html (string): HTML string of the email body to be sent.
        attachments (QuerySet): EmailDraftAttachment QuerySet.

    Returns:
        body_html (string),
        body_text (string),
        headers (dict)
    """
    if html is None:
        return None

    headers = []
    inline_images = []
    soup = create_a_beautiful_soup_object(html)

    if soup and attachments:
        inline_images = soup.findAll('img', {'cid': lambda cid: cid})

    if (not soup or soup.get_text() == '') and not inline_images:
        body_html = html
    else:
        cid_done = []

        for image in inline_images:
            image_cid = image['cid']

            for file in attachments:  # TODO: rename file.
                if (file.cid[1:-1] == image_cid or file.cid == image_cid) and file.cid not in cid_done:
                    image['src'] = "cid:%s" % image_cid

                    storage_file = default_storage._open(file.attachment.name)
                    filename = get_attachment_filename_from_url(file.attachment.name)

                    if hasattr(storage_file, 'key'):
                        content_type = storage_file.key.content_type
                    else:
                        content_type = mimetypes.guess_type(storage_file.file.name)[0]

                    storage_file.open()
                    content = storage_file.read()
                    storage_file.close()

                    response = {
                        'content-type': content_type,
                        'content-disposition': 'inline',
                        'content-filename': filename,
                        'content-id': file.cid,
                        'x-attachment-id': image_cid,
                        'content-transfer-encoding': 'base64',
                        'content': content
                    }

                    headers.append(response)
                    cid_done.append(file.cid)
                    del image['cid']

        body_html = soup.encode_contents()

    body_text_handler = html2text.HTML2Text()
    body_text_handler.ignore_links = True
    body_text_handler.body_width = 0
    body_text = body_text_handler.handle(html)

    return body_html, body_text, headers


# TODO: move to utils.
def get_mime_message_attachment(attachment):
    try:
        storage_file = default_storage._open(attachment.attachment.name)
    except IOError:
        # logger.exception('Couldn\'t get attachment, not sending %s' % self.id)
        return False  # TODO: other return value. Raise exception?

    filename = get_attachment_filename_from_url(attachment.attachment.name)

    storage_file.open()
    content = storage_file.read()
    storage_file.close()

    content_type, encoding = mimetypes.guess_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'text':
        msg = MIMEText(content, _subtype=sub_type)
    elif main_type == 'image':
        msg = MIMEImage(content, _subtype=sub_type)
    elif main_type == 'audio':
        msg = MIMEAudio(content, _subtype=sub_type)
    else:
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(content)
        Encoders.encode_base64(msg)

    msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))

    return msg


# TODO: move to utils.
def get_mime_message_inline(header):
    msg = None
    main_type, sub_type = header['content-type'].split('/', 1)
    if main_type == 'image':
        msg = MIMEImage(
            header['content'],
            _subtype=sub_type,
            name=os.path.basename(header['content-filename'])
        )
        msg.add_header(
            'Content-Disposition',
            header['content-disposition'],
            filename=os.path.basename(header['content-filename'])
        )
        msg.add_header('Content-ID', header['content-id'])

    return msg


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
            callback=parse_response(parse_message, message)
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
            callback=parse_response(parse_message, message)
        )

        return message

    def delete(self, remote_id):
        status_code = None

        self.batch.add(
            self.service.users().messages().delete(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_response(parse_deletion, status_code)
        )

        return status_code

    def untrash(self, remote_id):
        message = {}

        self.batch.add(
            self.service.users().messages().untrash(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_response(parse_message, message)
        )

        return message

    def label(self, remote_id, labels_add, labels_remove):
        """
        Update labels for email message.

        :param remote_id: id of the email message.
        :param labels_add: Labels to be added.
        :param labels_remove: Labels to be removed.

        :return: updated email message.
        """
        # TODO: Compare with add_and_remove_labels_for_message, why should we check if labels are actually present or not, just apply?

        if set(settings.GMAIL_LABELS_DONT_MANIPULATE) & set(labels_add) or set(
                settings.GMAIL_LABELS_DONT_MANIPULATE) & set(labels_remove):
            raise IllegalLabelException

        message = {}

        labels = {
            "addLabelIds": labels_add,
            "removeLabelIds": labels_remove
        }

        self.batch.add(
            self.service.users().messages().modify(
                userId=self.user_id,
                id=remote_id,
                body=labels
            ),
            callback=parse_response(parse_message, message)
        )

        return message

    def spam(self, remote_id):
        # TODO: Compare toggle_spam_email_message, why remove all other labels? Gmail doesn't do the either.
        return self.label(remote_id, [settings.GMAIL_LABEL_SPAM], [])

    def unspam(self, remote_id):
        return self.label(remote_id, [], [settings.GMAIL_LABEL_SPAM])

    def archive(self, remote_id):
        # TODO: Compare with current Lily, archive removes also current label.
        return self.label(remote_id, [], [settings.GMAIL_LABEL_INBOX])

    def unarchive(self, remote_id):
        return self.label(remote_id, [settings.GMAIL_LABEL_INBOX], [])

    def read(self, remote_id):
        return self.label(remote_id, [], [settings.GMAIL_LABEL_UNREAD])

    def unread(self, remote_id):
        return self.label(remote_id, [settings.GMAIL_LABEL_UNREAD], [])

    def important(self, remote_id):
        return self.label(remote_id, [settings.GMAIL_LABEL_IMPORTANT], [])

    def unimportant(self, remote_id):
        return self.label(remote_id, [], [settings.GMAIL_LABEL_IMPORTANT])

    def _get_message_string(self, draft):
        """
        :type  draft: EmailDraft
        :param draft:
        """
        from email_wrapper_lib.models.models import EmailDraftToEmailRecipient, EmailDraftAttachment  # TODO: fix import.
        #TODO: Email template attachments?

        email_message = SafeMIMEMultipart('related')
        email_message['Subject'] = draft.subject
        email_message['From'] = '"{0}" <{1}>'.format(draft.account.username, draft.account.user_id)  # TODO: Compare with current implementation.

        email_message['To'] = self._get_recipients(EmailDraftToEmailRecipient.TO, draft.id)
        cc_recipients_list = self._get_recipients(EmailDraftToEmailRecipient.CC, draft.id)
        if cc_recipients_list:
            email_message['cc'] = cc_recipients_list
        bcc_recipients_list = self._get_recipients(EmailDraftToEmailRecipient.BCC, draft.id)
        if bcc_recipients_list:
            email_message['cc'] = bcc_recipients_list

        attachments = EmailDraftAttachment.objects.filter(draft_id=draft.pk)
        # attachments = EmailDraftAttachment.objects.filter(draft_id=draft.pk, inline=True)  # TODO: possble?
        html, text, inline_headers = replace_cid_and_change_headers(draft.body_html, attachments)

        email_message_alternative = SafeMIMEMultipart('alternative')
        email_message.attach(email_message_alternative)

        email_message_text = SafeMIMEText(text, 'plain', 'utf-8')
        email_message_alternative.attach(email_message_text)

        email_message_html = SafeMIMEText(html, 'html', 'utf-8')
        email_message_alternative.attach(email_message_html)

        # Add the inline attachments to the email message.
        for header in inline_headers:
            mime_message = get_mime_message_inline(header)
            if mime_message:
                email_message.attach(mime_message)

        # Add the none-inline attachments to the email message.
        attachments = EmailDraftAttachment.objects.filter(draft_id=draft.pk, inline=False)
        for attachment in attachments:
            mime_message = get_mime_message_attachment(attachment)
            email_message.attach(mime_message)

        return email_message

    def _get_recipients(self, recipient_type, draft_id):
        from email_wrapper_lib.models.models import EmailDraftToEmailRecipient  # TODO: fix import.
        recipients = EmailDraftToEmailRecipient.objects.filter(
            draft=draft_id,
            recipient_type=recipient_type
        ).values_list('name', 'email_address')

        recipients_list = ['"{0}" <{1}>'.format(recipient[0], recipient[1]) for recipient in recipients]

        return ", ".join(recipients_list)

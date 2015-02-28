import logging
import StringIO
from datetime import datetime
from email.utils import getaddresses

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.html import escape
from imapclient import SEEN

from python_imap.folder import DRAFTS
from python_imap.utils import convert_html_to_text

from .models.models import EmailHeader, EmailAddressHeader, EmailAttachment, EmailMessage, \
    get_attachment_upload_path, EmailAddress
from .utils import replace_anchors_in_html, replace_cid_in_html

task_logger = logging.getLogger('celery_task')


class EmailMessageCreationError(Exception):
    pass


def get_headers_and_identifier(headers, sent_date, tenant_id):
    """
    Create EmailHeader objects from the provided headers and get the email identifier.

    Arguments:
        headers (dict): Dict containing the names and values for the EmailHeader objects
        sent_date (date): Sent date of email
        tenant_id (int): PK of the Tenant of the email account

    Returns:
        email_header_list (list): List containing EmailHeaders
        email_address_header_list (list): List containing EmailAddresHeaders
        message_identifier (str): The identifier of an emailmessage
    """
    # Remove certain headers that are stored in the model instead
    headers.pop('Received', None)
    headers.pop('Date', None)

    email_headers_list = []
    email_address_header_list = []
    message_identifier = None
    for name, value in headers.items():
        email_header = EmailHeader()
        email_header.name = name
        email_header.value = value
        email_headers_list.append(email_header)
        # For some headers we want to save it also in EmailAddressHeader model.
        if name in ['To', 'From', 'CC', 'Delivered-To', 'Sender']:
            email_addresses = getaddresses([value])
            for address_name, email_address in email_addresses:  # pylint: disable=W0612
                if email_address:
                    email_address_header = EmailAddressHeader()
                    email_address_header.name = name
                    email_address_header.value = value
                    email_address_header.email_address = EmailAddress.objects.get_or_create(
                        email_address=email_address.lower()
                    )[0]
                    email_address_header.sent_date = sent_date
                    email_address_header.tenant_id = tenant_id
                    email_address_header_list.append(email_address_header)
        elif name.lower() == 'message-id':
            message_identifier = value

    # Add message identifier to all email_address_headers
    for email_address_header in email_address_header_list:
        email_address_header.message_identifier = message_identifier

    return email_headers_list, email_address_header_list, message_identifier


def save_headers(messages, model):
    """
    Save email headers to the database.

    Arguments:
        headers (dict): Dictionary containing message_ids and headers
        model: The Model class that needs to be created
    """
    obj_list = []
    # Add header to object list
    for uid, messages in messages.items():
        for header in messages:
            obj_list.append(header)
    model.objects.bulk_create(obj_list)


def create_email_attachments(attachment_list, tenant_id, inline=False):
    """
    Create EmailAttachments.

    Arguments:
        attachment_list (list): List of raw email attachments
        tenant_id (int): id of the Tenant
        inline (boolean): True if attachments are inline

    Returns:
        email_attachment_list (list): list of EmailAttachments
    """
    email_attachment_list = []
    for attachment in attachment_list:
        if inline:
            cid, attachment = attachment
        else:
            cid = None
        file = StringIO.StringIO(attachment.get('payload'))
        file.content_type = attachment.get('content_type')
        file.size = attachment.get('size')
        file.name = attachment.get('name')

        email_attachment = EmailAttachment()
        email_attachment.attachment = file
        email_attachment.size = attachment.get('size')
        email_attachment.tenant_id = tenant_id
        email_attachment.inline = inline
        email_attachment.cid = cid
        email_attachment_list.append(email_attachment)

    return email_attachment_list


def save_email_message(message, account, folder, email_ctype):
    """
    Get or Create existing message or create a new one

    Arguments:
        message (instance): Message object
        account (instance): The email account instance to which every message will be linked
        folder (string): The remote folder where the message is stored
        email_ctype (integer): ctype id of the EmailMessage class

    Returns:
        email_headers (list): List of EmailHeaders
        email_address_headers (list): List of EmailAddressHeaders
        email_attachments (list): of List of EmailAttachments
        inline_email_attachments (list) of EmailAttachments
    """
    sent_date = message.get_sent_date()

    email_message = EmailMessage.objects.get_or_create(
        uid=message.uid,
        folder_name=folder.name_on_server,
        account=account,
        sent_date=sent_date,
        tenant=account.tenant,
    )[0]

    message_flags = message.get_flags()
    if message_flags:
        email_message.is_seen = SEEN in message_flags
        email_message.flags = message_flags

    body_html = message.get_html_body(remove_tags=settings.BLACKLISTED_EMAIL_TAGS)
    body_text = message.get_text_body()

    if body_html is not None and not body_text:
        body_text = convert_html_to_text(body_html, keep_linebreaks=True)
    elif body_text is not None:
        body_text = escape(body_text)

    # Check for headers
    headers = message.get_headers()
    email_headers = None
    email_address_headers = None
    if headers is not None:
        email_headers, email_address_headers, message_identifier = get_headers_and_identifier(
            headers,
            sent_date,
            account.tenant_id,
        )
        if message_identifier:
            email_message.message_identifier = message_identifier

    # Check if message is sent from account
    name, from_email = message.get_send_from()
    if account.email == from_email:
        email_message.sent_from_account = True

    email_message.body_html = replace_anchors_in_html(body_html)
    email_message.body_text = body_text
    email_message.size = message.get_size()
    email_message.folder_identifier = folder.identifier
    email_message.is_private = False
    email_message.tenant = account.tenant
    email_message.polymorphic_ctype = email_ctype
    email_message.save()

    # Check for attachments
    email_attachments = None
    attachments = message.get_attachments()
    if len(attachments):
        email_attachments = create_email_attachments(
            attachments,
            account.tenant_id
        )

    # Check for inline attachments
    inline_email_attachments = None
    inline_attachments = message.get_inline_attachments().items()
    if len(inline_attachments):
        inline_email_attachments = create_email_attachments(
            inline_attachments,
            account.tenant_id,
            inline=True
        )

    return email_headers, email_address_headers, email_attachments, inline_email_attachments


def save_attachments(attachments, tenant_id, folder, inline=False):
    """
    Save attachments.

    Arguments:
        attachments (dict): Dict of message_ids and attachment_list
        tenant_id (int): id of the Tenant
        folder (str): remote folder where attachment is stored
        inline (boolean): True if attachment is inline in emailmessage
    """
    for message_id, attachment_list in attachments.items():
        cid_attachments = {}
        for attachment in attachment_list:
            attachment.attachment = File(attachment.attachment, attachment.attachment.name)

            if inline:
                email_attachment = EmailAttachment.objects.get_or_create(
                    inline=True,
                    size=attachment.size,
                    message_id=attachment.message_id,
                    tenant_id=tenant_id
                )[0]
                email_attachment.attachment = attachment.attachment
                email_attachment.save()

                cid_attachments[attachment.cid] = email_attachment

            else:
                # Upload attachments that are new or if it belongs to a draft
                path = get_attachment_upload_path(attachment, attachment.attachment.name)
                if not default_storage.exists(path) or folder.identifier == DRAFTS:
                    attachment.save()
                else:
                    attachment.attachment.name = path

        # Replace img elements with the *cid* src attribute to they point to AWS
        if cid_attachments:
            email_message = attachment_list[0].message
            email_message.body_html = replace_cid_in_html(email_message.body_html, cid_attachments)
            email_message.save()


def create_headers_query_string(new_headers, existing_headers, table_name):
    """
    Create query string for headers dict.

    Arguments:
        new_headers (dict): Dict of headers
        existing_headers (dict): Dict of existing headers
        table_name (string): name of the table that needs to be updated

    Returns:
        total_query_string (str): custom query string
        param_list (list): list of parameters for query string
        query_count (int): number of queries in query string
    """
    header_obj_list = []
    # Add header to object list
    for uid, headers in new_headers.items():
        for header in headers:
            header_obj_list.append(header)

    # Build query string and parameter list
    total_query_string = ''
    param_list = []
    query_count = 0
    task_logger.debug('Looping through %s headers that need updating', len(header_obj_list))
    for header_obj in header_obj_list:
        # Decide whether to update or insert this email header
        if header_obj.name in existing_headers.get(header_obj.message_id, []):
            # Update email header
            query_string = 'UPDATE %s SET ' % table_name
            query_string += 'value = %s '

            query_string += 'WHERE name = %s AND message_id = %s;\n'
            param_list.append(header_obj.value)
            param_list.append(header_obj.name)
            param_list.append(header_obj.message_id)
        else:
            # Insert email header
            query_string = 'INSERT INTO %s ' % table_name
            query_string += '(name, value, message_id) VALUES (%s, %s, %s);\n'
            param_list.append(header_obj.name)
            param_list.append(header_obj.value)
            param_list.append(header_obj.message_id)

        total_query_string += query_string
        query_count += 1

    return total_query_string, param_list, query_count


def create_message_query_string(message, account_id, folder_name):
    """
    Create query string for message.

    Arguments:
        message (instance): Message object
        account_id (int): id of the account
        folder_name (string): name of de folder on the server

    Returns:
        total_query_string (str): custom query string
        params_list (list): list of parameters for query string
        query_count (int): number of queries in query string
    """
    param_list = []
    total_query_string = ''
    query_count = 0
    query_string = 'UPDATE email_emailmessage SET is_deleted = FALSE, '

    message_flags = message.get_flags()
    if message_flags:
        query_string += 'flags = %s, '
        param_list.append(str(message_flags))

    body_html = message.get_html_body(remove_tags=settings.BLACKLISTED_EMAIL_TAGS)
    body_text = message.get_text_body()

    if body_html is not None and not body_text:
        body_text = convert_html_to_text(body_html, keep_linebreaks=True)

    if body_html is not None:
        query_string += 'body_html = %s, '
        param_list.append(replace_anchors_in_html(body_html))

    if body_text is not None:
        query_string += 'body_text = %s, '
        param_list.append(escape(body_text))

    if query_string.endswith(', '):
        query_string = query_string.rstrip(', ')
        query_string += ' WHERE account_id = %s AND uid = %s AND folder_name = %s;\n'
        param_list.append(account_id)
        param_list.append(message.uid)
        param_list.append(folder_name)

        total_query_string += query_string
        query_count += 1

    message_sent_date = message.get_sent_date()
    query_string = 'UPDATE messaging_message SET '

    if message_flags:
        query_string += 'is_seen = %s, '
        param_list.append(SEEN in message_flags)

    query_string += 'sent_date = %s'
    param_list.append(datetime.strftime(message_sent_date, '%Y-%m-%d %H:%M:%S%z'))

    query_string += ' WHERE historylistitem_ptr_id = (SELECT message_ptr_id FROM email_emailmessage WHERE account_id = %s AND uid = %s AND folder_name = %s);\n'
    param_list.append(account_id)
    param_list.append(message.uid)
    param_list.append(folder_name)

    total_query_string += query_string
    query_count += 1

    return total_query_string, param_list, query_count

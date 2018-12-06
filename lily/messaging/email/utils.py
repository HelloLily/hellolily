import logging
import re
import mimetypes
import anyjson
import json
import os

from datetime import datetime
from bs4 import BeautifulSoup, UnicodeDammit
import html2text
from urllib import unquote

from django.apps import apps
from django.db.models.query_utils import Q
from django.conf import settings
from django.core.files.storage import default_storage
from django.urls import reverse
from django.template import Context
from django.template.base import VARIABLE_TAG_START, VARIABLE_TAG_END
from django.template.loader_tags import BlockNode, ExtendsNode
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from jinja2.sandbox import SandboxedEnvironment
from jinja2 import TemplateSyntaxError

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.search.scan_search import ModelMappings
from lily.search.indexing import update_in_index

from .models.models import EmailAttachment, EmailMessage, EmailAccount, SharedEmailConfig
from .sanitize import sanitize_html_email

_EMAIL_PARAMETER_DICT = {}
_EMAIL_PARAMETER_API_DICT = {}
_EMAIL_PARAMETER_CHOICES = {}

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'tests/data')

DRAFTS = '\\Drafts'
INBOX = '\\Inbox'
SENT = '\\Sent'
SPAM = '\\Spam'
TRASH = '\\Trash'


def get_field_names(field):
    """
    Return the field name and the verbose field name.

    :param field: The field from which we want the name
    :return: The field name and the verbose field name
    """
    return field, field.replace('_', ' ')


def get_email_parameter_dict():
    """
    If there is no email parameter dict yet, construct it and return it.
    The email parameter dict consists of all posible variables for email templates.

    This function returns parameters organized by variable name for easy parsing.
    """
    if not _EMAIL_PARAMETER_DICT:
        for model in apps.get_models():
            if hasattr(model, 'EMAIL_TEMPLATE_PARAMETERS'):
                for field in model.EMAIL_TEMPLATE_PARAMETERS:
                    field_name, field_verbose_name = get_field_names(field)

                    _EMAIL_PARAMETER_DICT.update({
                        '%s.%s' % (model._meta.verbose_name.lower(), field_name.lower()): {
                            'model': model,
                            'model_verbose': model._meta.verbose_name.capitalize(),
                            'field': field,
                            'field_verbose': field_verbose_name.capitalize(),
                        }
                    })
    return _EMAIL_PARAMETER_DICT


def get_email_parameter_api_dict():
    """
    If there is no email parameter dict yet, construct it and return it.
    The email parameter dict consists of all possible variables for email templates.

    This function returns parameters organized by variable name for easy parsing.
    """
    if not _EMAIL_PARAMETER_API_DICT:
        for model in apps.get_models():
            if hasattr(model, 'EMAIL_TEMPLATE_PARAMETERS'):
                for field in model.EMAIL_TEMPLATE_PARAMETERS:
                    field_name, field_verbose_name = get_field_names(field)

                    key = '%s.%s' % (model._meta.verbose_name.lower(), field_name.lower())
                    _EMAIL_PARAMETER_API_DICT.setdefault(model._meta.verbose_name.capitalize(), {}).update({
                        key: field_verbose_name.capitalize()
                    })
    return _EMAIL_PARAMETER_API_DICT


def get_email_parameter_choices():
    """
    If there is no email parameter choices yet, construct it and return it.
    The email parameter choices consists of all possible variables for email templates.

    This function returns parameters organized by model name, for easy selecting.
    """
    if not _EMAIL_PARAMETER_CHOICES:
        for model in apps.get_models():
            if hasattr(model, 'EMAIL_TEMPLATE_PARAMETERS'):
                for field in model.EMAIL_TEMPLATE_PARAMETERS:
                    field_name, field_verbose_name = get_field_names(field)

                    key = '%s.%s' % (model._meta.verbose_name.lower(), field_name.lower())
                    if '%s' % model._meta.verbose_name.capitalize() in _EMAIL_PARAMETER_CHOICES:
                        _EMAIL_PARAMETER_CHOICES.get('%s' % model._meta.verbose_name.capitalize()).update({
                            key: field_verbose_name.capitalize(),
                        })
                    else:
                        _EMAIL_PARAMETER_CHOICES.update({
                            '%s' % model._meta.verbose_name.capitalize(): {
                                key: field_verbose_name.capitalize(),
                            }
                        })
    return _EMAIL_PARAMETER_CHOICES


class TemplateParser(object):
    """
    Parse template input and provide helper functions for further template handling.
    """

    def __init__(self, text):
        self.valid_parameters = []
        self.valid_blocks = []

        text = self._escape_text(text.encode('utf-8')).strip()
        text = text.decode('utf-8')
        template_environment = SandboxedEnvironment()

        try:
            self.template = template_environment.from_string(text)
            self.error = None
        except TemplateSyntaxError as e:
            self.template = None
            self.error = e

    def is_valid(self):
        """
        Return wheter the template is valid or not.
        """
        return self.template and not self.error

    def get_text(self):
        """
        Return the unrendered text, so variables etc. are still visible.
        """
        return self.template.render(context={})

    def get_parts(self, default_part='body_html', parts=None):
        """
        Return the contents of specified parts, if no parts are available return the default part.

        :param default_part: which part is filled when no parts are defined.
        :param parts: override the default recognized parts.
        """
        parts = parts or ['name', 'subject', 'body_html']
        response = {}

        for part in parts:
            value = self._get_node(self.template, name=part).strip()

            if value:
                response[part] = value

        if not response:
            response[default_part] = self.get_text()

        return response

    def _escape_text(self, text):
        """
        Escape variables and delete Django syntax around variables that are not allowed.
        """
        # Filter on parameters with the following syntax: model.field
        param_regex = (re.compile('(%s[\s]*[a-zA-Z]+\.[a-zA-Z_]+[\s]*%s)' % (
            re.escape(VARIABLE_TAG_START),
            re.escape(VARIABLE_TAG_END)
        )))
        parameter_list = [x for x in re.findall(param_regex, text)]

        for parameter in parameter_list:
            stripped_parameter = parameter.strip(' {}')
            split_parameter = stripped_parameter.split('|')[0]
            if split_parameter in get_email_parameter_dict():
                # variable is accepted, now just escape so it can be rendered later
                text = text.replace(
                    '%s' % parameter,
                    '{%% templatetag openvariable %%} %s {%% templatetag closevariable %%}' % stripped_parameter
                )
                self.valid_parameters.append(stripped_parameter)
            else:
                # variable is not accepted, remove surrounding braces
                text = text.replace('%s' % parameter, '%s' % stripped_parameter)

        return text

    def _get_node(self, template, context=Context(), name='subject', block_lookups=None):
        """
        Get contents of specified node out of the template.
        """
        block_lookups = block_lookups or {}
        for node in template:
            if isinstance(node, BlockNode) and node.name == name:
                # Rudimentary handling of extended templates, for issue #3
                for i in xrange(len(node.nodelist)):
                    n = node.nodelist[i]
                    if isinstance(n, BlockNode) and n.name in block_lookups:
                        node.nodelist[i] = block_lookups[n.name]
                return node.render(context)
            elif isinstance(node, ExtendsNode):
                lookups = dict([(n.name, n) for n in node.nodelist if isinstance(n, BlockNode)])
                lookups.update(block_lookups)
                return self._get_node(node.get_parent(context), context, name, lookups)
        return ''


def get_attachment_filename_from_url(url):
    return unquote(url).split('/')[-1]


def render_email_body(html, mapped_attachments, request):
    """
    Update all the target attributes in the <a> tag.
    After that replace the cid information in the html.

    Args:
        html (string): HTML string of the email body to be sent.
        mapped_attachments (list): List of linked attachments to the email.
        request (instance): The Django request.

    Returns:
        html body (string)
    """
    if html is None:
        return None

    email_body = extract_script_tags(html)
    email_body = replace_anchors_in_html(email_body)
    email_body = replace_cid_in_html(email_body, mapped_attachments, request)

    return email_body


def replace_cid_in_html(html, mapped_attachments, request):
    """
    Replace all the cid image information with a link to the image

    Args:
        html (string): HTML string of the email body to be sent.
        mapped_attachments (list): List of linked attachments to the email.
        request (instance): The Django request.

    Returns:
        html body (string)
    """
    if html is None:
        return None

    soup = create_a_beautiful_soup_object(html)
    cid_done = []
    inline_images = []

    if soup and mapped_attachments:
        inline_images = soup.findAll('img', {'src': lambda src: src and src.startswith('cid:')})

    if (not soup or soup.get_text() == '') and not inline_images:
        html = sanitize_html_email(html)
        return html

    protocol = 'http'
    if request.is_secure():
        protocol = 'https'
    host = request.META['HTTP_HOST']

    for image in inline_images:
        image_cid = image.get('src')[4:]

        for attachment in mapped_attachments:
            if (attachment.cid[1:-1] == image_cid or attachment.cid == image_cid) and attachment.cid not in cid_done:
                proxy_url = reverse('email_attachment_proxy_view', kwargs={'pk': attachment.pk})
                image['src'] = '%s://%s%s' % (protocol, host, proxy_url)
                image['cid'] = image_cid
                cid_done.append(attachment.cid)

    html = soup.encode_contents()
    html = sanitize_html_email(html)

    return html


def replace_cid_and_change_headers(html, pk):
    """
    Check in the html source if there is an image tag with the attribute cid.
    Loop through the attachments that are linked with the email. If there is a
    match replace the source of the image with the cid information. After read
    the image information from the disk and put the data in a dummy header.
    At least create a plain text version of the html email.

    Args:
        html (string): HTML string of the email body to be sent.
        mapped_attachments (list): List of linked attachments to the email.
        request (instance): The Django request.

    Returns:
        body_html (string),
        body_text (string),
        dummy_headers (dict)
    """
    if html is None:
        return None

    dummy_headers = []
    inline_images = []
    soup = create_a_beautiful_soup_object(html)

    attachments = []
    if pk:
        attachments = EmailAttachment.objects.filter(message_id=pk)

    if soup and attachments:
        inline_images = soup.findAll('img', {'cid': lambda cid: cid})

    if (not soup or soup.get_text() == '') and not inline_images:
        body_html = html
    else:
        cid_done = []

        for image in inline_images:
            image_cid = image['cid']

            for file in attachments:
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

                    dummy_headers.append(response)
                    cid_done.append(file.cid)
                    del image['cid']

        body_html = soup.encode_contents()

    body_text_handler = html2text.HTML2Text()
    body_text_handler.ignore_links = True
    body_text_handler.body_width = 0
    body_text = body_text_handler.handle(html)

    # After django 1.11 update forcing the html part of the body to be unicode is needed to avoid encoding errors.
    dammit = UnicodeDammit(body_html)
    encoding = dammit.original_encoding
    if encoding:
        body_html = body_html.decode(encoding)

    return body_html, body_text, dummy_headers


def create_a_beautiful_soup_object(html):
    """
    Try to create a BeautifulSoup object that has not an empty body
    If so try a different HTML parser.

    Args:
        html (string): HTML string of the email body to be sent.

    Returns:
        soup (BeautifulSoup object or None)
    """
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

    if soup.get_text() == '':
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

        if soup.get_text() == '':
            soup = BeautifulSoup(html, 'html5lib')

            if soup.get_text() == '':
                soup = BeautifulSoup(html, 'xml', from_encoding='utf-8')

                if soup.get_text == '':
                    soup = None

    return soup


def replace_anchors_in_html(html):
    """
    Make all anchors open outside the iframe.
    """
    if html is None:
        return None

    soup = create_a_beautiful_soup_object(html)

    if not soup or soup.get_text == '':
        return html

    for anchor in soup.findAll('a'):
        anchor.attrs.update({
            'target': '_blank',
            'rel': 'noopener noreferrer',
        })

    return soup.encode_contents()


def extract_script_tags(html):
    if html is None:
        return None

    soup = create_a_beautiful_soup_object(html)

    if not soup or soup.get_text == '':
        return html

    for item in soup.findAll('script'):
        item.extract()

    return soup.encode_contents()


def create_reply_body_header(email_message):
    """
    Create a body reply header with a date and name

    Args:
        object (dict): EmailMessage reference

    Returns:
        Text string

    """
    reply_string = _('%(sender)s (%(email_address)s) wrote on %(date)s:') % {
        'date': email_message.sent_date.strftime("%d %B %Y %H:%M"),
        'sender': email_message.sender.name,
        'email_address': email_message.sender.email_address
    }
    reply_header = ('<br /><br />' +
                    reply_string +
                    '<hr />')

    return reply_header


def create_recipients(receivers, filter_emails=[]):
    """
    Converts Select2 ready recipients based on the received_by and/or received_by_cc of an email

    Arguments:
        receivers (list): list of Recipient objects
        filter_emails (list, optional): list of email addresses that shouldn't be converted

    Returns:
        recipients (list):
    """
    recipients = []
    email_addresses = []

    if not isinstance(filter_emails, list):
        filter_emails = [filter_emails]

    for receiver in receivers:
        # TODO: Once we correct the sync we probably won't need this check
        if receiver.email_address in email_addresses or receiver.email_address in filter_emails:
            continue

        name = receiver.name

        if not name:
            # If no name was synced try to load a contact
            recipient = Contact.objects.filter(email_addresses__email_address=receiver.email_address).order_by(
                'created').first()

            if recipient:
                # If contact exists, set contact's full name as name
                name = recipient.full_name
            else:
                recipient = Account.objects.filter(email_addresses__email_address=receiver.email_address).order_by(
                    'created').first()

                if recipient:
                    # Otherwise if account exists, set account's name as name
                    name = recipient.name

        if name:
            # If a name is available we setup the select2 field differently
            recipients.append({
                'id': '"' + name + '" <' + receiver.email_address + '>',
                'text': name + ' <' + receiver.email_address + '>'
            })
        else:
            # Otherwise only display the email address
            recipients.append({
                'id': receiver.email_address,
                'text': receiver.email_address
            })

        email_addresses.append(receiver.email_address)

    return recipients


def reindex_email_message(instance):
    """
    Re-index the given email message instance, so there is no need to misuse the save method for triggering a re-index.

    No need to check related models compared to the more generic post_save signal. Email messages have no related model
    mapping.
    """
    if settings.ES_DISABLED:
        return
    if not isinstance(instance, EmailMessage):
        return
    mapping = ModelMappings.model_to_mappings.get(type(instance))
    if mapping:
        update_in_index(instance, mapping)


def fullpath(filename):
    return os.path.join(DATA_DIR, "{:%H%M%S%f}".format(datetime.now()) + '-' + filename)


def write_json_to_disk(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        logger.info("JSON written: %s" % path)


def get_filtered_message(email_message, email_account, user):
    shared_config = email_account.sharedemailconfig_set.filter(user=user).first()

    # If the email account or sharing is set to 'metadata' only return these fields.
    metadata_only_message = {
        'id': email_message.id,
        'sender': email_message.sender,
        'received_by': email_message.received_by.all(),
        'received_by_cc': email_message.received_by_cc.all(),
        'sent_date': email_message.sent_date,
        'account': email_message.account,
    }

    if email_account.owner != user:
        if shared_config:
            privacy = shared_config.privacy
        else:
            privacy = email_account.privacy

        if privacy == EmailAccount.METADATA:
            return metadata_only_message
        elif privacy == EmailAccount.PRIVATE:
            # Sharing for this user is set to private, so don't return a message.
            return None
        else:
            return email_message

    return email_message


def convert_br_to_newline(soup, newline='\n'):
    """
    Replace html line breaks with spaces to prevent lines appended after one another.
    """
    for linebreak in soup.find_all('br'):
        linebreak.replaceWith(newline)

    return soup


def get_extensions_for_type(general_type):
    # For known mimetypes, use some extensions we know to be good or we prefer
    # above others.. This solves some issues when the first of the available
    # extensions doesn't make any sense, e.g.
    # >>> get_extensions_for_type('txt')
    # 'asc'
    preferred_types_map = {
        'text/plain': '.txt',
        'text/html': '.html',
    }

    if general_type in preferred_types_map:
        yield preferred_types_map[general_type]

    if not mimetypes.inited:
        mimetypes.init()

    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext] == general_type or mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext

    # return at least an extension for unknown mimetypes
    yield '.bak'


def get_shared_email_accounts(user):
    if not user.tenant.billing.is_free_plan:
        # Team plan allows sharing of email account.
        # Get a list of email accounts which are publicly shared or shared specifically with the user.
        shared_email_account_list = EmailAccount.objects.filter(
            Q(owner=user) |
            Q(privacy=EmailAccount.PUBLIC) |
            (Q(sharedemailconfig__user__id=user.pk) & Q(sharedemailconfig__privacy=EmailAccount.PUBLIC))
        )
    else:
        # Free plan, so only allow own email accounts.
        shared_email_account_list = EmailAccount.objects.filter(
            Q(owner=user),
        )

    shared_email_account_list = shared_email_account_list.filter(
        tenant=user.tenant,
        is_deleted=False,
    ).distinct('id')

    # Get a list of email accounts the user doesn't want to follow.
    email_account_exclude_list = SharedEmailConfig.objects.filter(
        user=user,
        is_hidden=True
    ).values_list('email_account_id', flat=True)

    # Exclude those email accounts from the accounts that are shared with the user.
    # So it's a list of email accounts the user wants to follow or is allowed to view.
    email_account_list = shared_email_account_list.exclude(
        id__in=email_account_exclude_list
    )

    return email_account_list


def limit_email_accounts(tenant):
    # Free plan has a limit of two email accounts.
    email_accounts = EmailAccount.objects.filter(tenant=tenant, is_deleted=False).order_by('created')

    # Sharing isn't part of the free plan, so set first two email accounts to private.
    for email_account in email_accounts[:2]:
        email_account.previous_privacy = email_account.privacy
        email_account.privacy = EmailAccount.PRIVATE
        email_account.save()

    # Free plan has a limit of two email accounts.
    # So disable all other email accounts.
    for email_account in email_accounts[2:]:
        email_account.is_active = False
        email_account.save()


def restore_email_account_settings(tenant):
    email_accounts = EmailAccount.objects.filter(tenant=tenant, is_deleted=False)

    # Set back the email accounts to their previous settings.
    for email_account in email_accounts:
        if email_account.previous_privacy is not None:
            email_account.privacy = email_account.previous_privacy
            email_account.previous_privacy = None

        email_account.is_active = True
        email_account.save()


def determine_message_type(thread_id, sent_date, email_address):
    """
    Determine if the message is a reply, reply-all, forward, forward-multi or just a normal email.
    Return the message type and the message id it's a reply to, or forward of.
    """
    # Get the whole thread this message belongs to.
    thread = EmailMessage.objects.filter(thread_id=thread_id)

    # Restrict the thread to only older messages.
    thread = thread.filter(sent_date__gt=sent_date).order_by('sent_date')

    # Restrict the thread to just the outgoing messages.
    email = thread.filter(sender__email_address=email_address)

    # And retrieve only necessary fields.
    email = email.only('id', 'subject', 'received_by', 'received_by_cc')

    # And we only want the first one.
    email = email.first()

    if email:
        receivers = set(email.received_by.all()) | set(email.received_by_cc.all())
        numbers_of_receivers = len(receivers)

        if email.subject.startswith('Re: '):
            if numbers_of_receivers == 1:
                return EmailMessage.REPLY, email.id
            else:
                return EmailMessage.REPLY_ALL, email.id
        elif email.subject.startswith('Fwd: '):
                if numbers_of_receivers == 1:
                    return EmailMessage.FORWARD, email.id
                else:
                    return EmailMessage.FORWARD_MULTI, email.id

    return EmailMessage.NORMAL, None


def get_formatted_reply_email_subject(subject, prefix='Re: '):
    while True:
        if subject.lower().startswith('re:') or subject.lower().startswith('fw:'):
            subject = subject[3:].lstrip()
        elif subject.lower().startswith('fwd:'):
            subject = subject[4:].lstrip()
        else:
            break

    return '{}{}'.encode('utf-8').format(prefix, subject)


def get_formatted_email_body(action, email_message):
    body_header = create_reply_body_header(email_message)

    if action in ['forward', 'forward-multi']:
        forward_header_to = []
        for recipient in email_message.received_by.all():
            if recipient.name:
                forward_header_to.append('{} &lt;{}&gt;'.format(
                    recipient.name.encode('utf-8'),
                    recipient.email_address.encode('utf-8'))
                )
            else:
                forward_header_to.append(recipient.email_address.encode('utf-8'))

        body_header = (
            '<br /><br />'
            '<hr />'
            '---------- Forwarded message ---------- <br />'
            'From: {from_email}<br/>'
            'Date: {date}<br/>'
            'Subject: {subject}<br/>'
            'To: {to}<br />'
        ).format(
            from_email=email_message.sender.email_address,
            date=email_message.sent_date.ctime(),
            subject=get_formatted_reply_email_subject(email_message.subject, prefix=''),
            to=', '.join(forward_header_to)
        )

    return body_header + mark_safe(email_message.reply_body)


class EmailHeaderInputException(Exception):
    pass


def get_email_headers(action, email_message=None):
    """ Returns the email headers for all actions. """
    headers = {}
    if action == 'compose':
        return headers

    if action != 'compose' and email_message is None:
        raise EmailHeaderInputException()

    message_id = email_message.get_message_id()
    if action in ['reply', 'reply_all', 'forward', 'forward-multi']:
        headers['References'] = message_id
    if action in ['reply', 'reply-all']:
        headers['In-Reply-To'] = message_id

    return anyjson.dumps(headers)

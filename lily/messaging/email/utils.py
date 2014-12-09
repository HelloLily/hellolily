import re
import socket

from datetime import datetime, timedelta
from smtplib import SMTPAuthenticationError
from types import FunctionType
from urllib import unquote

from bs4 import BeautifulSoup
from celery import signature
from celery.states import PENDING
from dateutil.tz import tzutc
from django.conf import settings

from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart, get_connection
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Field
from django.db.models.query_utils import Q
from django.template.defaultfilters import truncatechars
from django.template import (Context, TemplateSyntaxError, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START,
                             VARIABLE_TAG_END)
from django.template.loader import get_template_from_string
from django.template.loader_tags import BlockNode, ExtendsNode
from django.utils.translation import ugettext as _

from lily.messaging.email.decorators import get_safe_template
from lily.messaging.email.models import EmailAccount, EmailMessage
from lily.messaging.utils import get_messages_accounts
from lily.tenant.middleware import get_current_user
from python_imap.errors import IMAPConnectionError
from python_imap.folder import INBOX
from python_imap.server import IMAP
from taskmonitor.models import TaskStatus
from taskmonitor.utils import resolve_annotations


_EMAIL_PARAMETER_DICT = {}
_EMAIL_PARAMETER_CHOICES = {}


def get_field_names(field):
    """
    Return the field name and the verbose field name.

    :param field: The field from which we want the name
    :return: The field name and the verbose field name
    """
    return field, field.replace('_', ' ')


def get_email_parameter_dict():
    """
    If there is no e-mail parameter dict yet, construct it and return it.
    The e-mail parameter dict consists of all posible variables for e-mail templates.

    This function returns parameters organized by variable name for easy parsing.

    """
    if not _EMAIL_PARAMETER_DICT:
        for model in models.get_models():
            if hasattr(model, 'EMAIL_TEMPLATE_PARAMETERS'):
                for field in model.EMAIL_TEMPLATE_PARAMETERS:
                    field_name, field_verbose_name = get_field_names(field)

                    _EMAIL_PARAMETER_DICT.update({
                        '%s_%s' % (model._meta.verbose_name.lower(), field_name.lower()): {
                            'model': model,
                            'model_verbose': model._meta.verbose_name.title(),
                            'field': field,
                            'field_verbose': field_verbose_name.title(),
                        }
                    })
    return _EMAIL_PARAMETER_DICT


def get_email_parameter_choices():
    """
    If there is no e-mail parameter choices yet, construct it and return it.
    The e-mail parameter choices consists of all possible variables for e-mail templates.

    This function returns parameters organized by model name, for easy selecting.

    """
    if not _EMAIL_PARAMETER_CHOICES:
        for model in models.get_models():
            if hasattr(model, 'EMAIL_TEMPLATE_PARAMETERS'):
                for field in model.EMAIL_TEMPLATE_PARAMETERS:
                    field_name, field_verbose_name = get_field_names(field)

                    if '%s' % model._meta.verbose_name.title() in _EMAIL_PARAMETER_CHOICES:
                        _EMAIL_PARAMETER_CHOICES.get('%s' % model._meta.verbose_name.title()).update({
                            '%s_%s' % (model._meta.verbose_name.lower(), field_name.lower()): field_verbose_name.title(),
                        })
                    else:
                        _EMAIL_PARAMETER_CHOICES.update({
                            '%s' % model._meta.verbose_name.title(): {
                                '%s_%s' % (model._meta.verbose_name.lower(), field_name.lower()): field_verbose_name.title(),
                            }
                        })
    return _EMAIL_PARAMETER_CHOICES


def get_folder_unread_count(folder, email_accounts=None):
    """
    Return the number of unread email messages in folder for given email accounts.
    """
    from lily.messaging.email.models import EmailAccount, EmailMessage  # prevent circular dependency
    if email_accounts is None:
        email_accounts = get_messages_accounts(user=get_current_user(), model_cls=EmailAccount).get_real_instances()

    return EmailMessage.objects.filter(Q(folder_identifier=folder) | Q(folder_name=folder), account__in=email_accounts, is_seen=False).count()


class TemplateParser(object):
    """
    Parse template input and provide helper functions for further template handling.
    """
    def __init__(self, text):
        self.valid_parameters = []
        self.valid_blocks = []

        text = self._escape_text(text.encode('utf-8')).strip()
        tags_whitelist = [
            'block', 'now', 'templatetag'
        ]
        safe_get_template_from_string = get_safe_template(tags=tags_whitelist)(get_template_from_string)

        try:
            self.template = safe_get_template_from_string(text)
            self.error = None
        except TemplateSyntaxError, e:
            self.template = None
            self.error = e

    def render(self, request, context=None):
        """
        Render the template in a form that is ready for output.

        :param request: request that is used to fill context.
        :param context: override the default context.
        """
        context = context or self.get_template_context(request)
        return get_template_from_string(self.get_text()).render(context=Context(context))

    def is_valid(self):
        """
        Return wheter the template is valid or not.
        """
        return self.template and not self.error

    def get_text(self):
        """
        Return the unrendered text, so variables etc. are still visible.
        """
        return self.template.render(context=Context())

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

    def get_template_context(self, request):
        """
        Retrieve the context used for rendering of the template in a dict.
        """
        parameters = self.valid_parameters
        param_dict = get_email_parameter_dict()
        result_dict = {}
        filled_param_dict = {}

        # Get needed results from database
        for param in parameters:
            model = param_dict[param]['model']
            field = param_dict[param]['field']
            lookup = model.EMAIL_TEMPLATE_LOOKUP

            if model not in result_dict:
                result_dict.update({
                    '%s' % model: eval(lookup)
                })
            field_name, field_verbose_name = get_field_names(field)
            filled_param_dict.update({
                '%s' % param: getattr(result_dict['%s' % model], field_name),
            })

        return filled_param_dict

    def get_parameter_list(self, text):
        """
        Retrieve all parameters using a regex.
        """
        param_re = (re.compile('(%s[\s]*[a-zA-Z_|]+[\s]*%s)' % (re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END))))

        return [x for x in re.findall(param_re, text)]

    def get_block_list(self, text):
        """
        Retrieve all tags using a regex.
        """
        param_re = (re.compile('(%s[\s]*.*[\s]*%s)' % (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

        return [x for x in re.findall(param_re, text)]

    def _escape_text(self, text):
        """
        Escape variables and delete django syntax around variables that are not allowed.
        """
        for parameter in self.get_parameter_list(text):
            stripped_parameter = parameter.strip(' {}')
            split_parameter = stripped_parameter.split('|')[0]
            if split_parameter in get_email_parameter_dict():
                # variable is accepted, now just escape so it can be rendered later
                text = text.replace('%s' % parameter, '{%% templatetag openvariable %%} %s {%% templatetag closevariable %%}' % stripped_parameter)
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
                #Rudimentary handling of extended templates, for issue #3
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


def replace_cid_in_html(html, mapped_attachments):
    if html is None:
        return None

    soup = BeautifulSoup(html)

    inline_images = soup.findAll('img', {'src': lambda src: src and src.startswith('cid:')})

    for image in inline_images:
        inline_attachment = mapped_attachments.get(image.get('src')[4:])
        if inline_attachment is not None:
            image['src'] = reverse('email_attachment_proxy_view', kwargs={'pk': inline_attachment.pk})

    return soup.encode_contents()


def replace_anchors_in_html(html):
    """
    Make all anchors open outside the iframe
    """
    if html is None:
        return None

    soup = BeautifulSoup(html)

    for anchor in soup.findAll('a'):
        anchor.attrs.update({
            'target': '_blank',
        })

    return soup.encode_contents()


def smtp_connect(account, fail_silently=True):
    kwargs = {
        'host': account.provider.smtp_host,
        'port': account.provider.smtp_port,
        'username': account.username,
        'password': account.password,
        'use_tls': account.provider.smtp_ssl,
    }

    return get_connection('django.core.mail.backends.smtp.EmailBackend', fail_silently=fail_silently, **kwargs)


class EmailMultiRelated(EmailMultiAlternatives):
    """
    A version of EmailMessage that makes it easy to send multipart/related
    messages. For example, including text and HTML versions with inline images.

    A Utility class for sending HTML emails with inline images
    http://hunterford.me/html-emails-with-inline-images-in-django/
    """
    related_subtype = 'related'

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, alternatives=None, cc=None):
        self.related_attachments = []
        return super(EmailMultiRelated, self).__init__(subject, body, from_email, to, bcc, connection, attachments, headers, alternatives, cc)

    def attach_related(self, filename=None, content=None, mimetype=None):
        """
        Attaches a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.
        """
        self.related_attachments.append((filename, content, mimetype))

    def _create_message(self, msg):
        return self._create_attachments(self._create_related_attachments(self._create_alternatives(msg)))

    def _create_alternatives(self, msg):
        for i, (content, mimetype) in enumerate(self.alternatives):
            if mimetype == 'text/html':
                self.alternatives[i] = (content, mimetype)

        return super(EmailMultiRelated, self)._create_alternatives(msg)

    def _create_related_attachments(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        if self.related_attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.related_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for related in self.related_attachments:
                msg.attach(self._create_related_attachment(*related))
        return msg

    def _create_related_attachment(self, filename, content, mimetype=None):
        """
        Convert the filename, content, mimetype triple into a MIME attachment
        object. Adjust headers to use Content-ID where applicable.
        Taken from http://code.djangoproject.com/ticket/4771
        """
        attachment = super(EmailMultiRelated, self)._create_attachment(filename, content, mimetype)
        if filename:
            mimetype = attachment['Content-Type']
            del attachment['Content-Type']
            del attachment['Content-Disposition']
            attachment.add_header('Content-Disposition', 'inline', filename=filename)
            attachment.add_header('Content-Type', mimetype, name=filename)
            attachment.add_header('Content-ID', '<%s>' % filename)
        return attachment


def get_full_folder_name_by_identifier(identifier, folder_data):
    folder_data = folder_data.items()

    for folder, values in folder_data:  # pylint: disable=W0612
        flags = values.get('flags')

        # Check if current flags contain identifier
        if identifier in flags:
            # Return folder name if found
            return values.get('full_name')

        # Otherwise check if the current folder has sub folders
        if values.get('is_parent'):
            # If folder has sub folders, recursive call to this function and check sub folders
            return get_full_folder_name_by_identifier(identifier, values.get('children'))

    return None


class LilyIMAP(IMAP):
    """
    Wrapper for `IMAP` to increase ease of use.
    """
    def __init__(self, account):
        host = account.provider.imap_host
        port = account.provider.imap_port
        ssl = account.provider.imap_ssl
        super(LilyIMAP, self).__init__(host, port=port, ssl=ssl, silent_fail=True)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.logout()


def verify_imap_credentials(imap_host, imap_port, imap_ssl, username, password):
    """
    Verify IMAP connection and credentials.

    Arguments:
        imap_host (str): address of host
        imap_port (int): port to connect to
        imap_ssl (boolean): True if ssl should be used
        username (str): username for login to IMAP client
        password (str): password for login to IMAP client

    Raises:
        ValidationError: If connection or login failed
    """
    # Resolve host name
    try:
        socket.gethostbyname(imap_host)
    except Exception:
        raise ValidationError(
            _('Could not resolve %(imap_host)s'),
            code='invalid_host',
            params={'imap_host': imap_host}
        )

    # Try connecting
    try:
        imap = IMAP(imap_host, imap_port, imap_ssl)
    except IMAPConnectionError:
        raise ValidationError(
            _('Could not connect to %(imap_host)s:%(imap_port)s'),
            code='invalid_connection',
            params={'imap_host': imap_host, 'imap_port': imap_port}
        )

    # Try login
    if not imap.login(username, password):
        raise ValidationError(
            _('Unable to login with provided username and password on the IMAP host'),
            code='invalid_credentials'
        )


def verify_smtp_credentials(smtp_host, smtp_port, use_tls, username, password):
    """
    Verify SMTP connection and credentials.

    Arguments:
        smtp_host (str): address of host
        smtp_port (int): port to connect to
        use_tls (boolean): True if tls should be used
        username (str): username for login to SMTP client
        password (str): password for login to SMTP client

    Raises:
        ValidationError: If connection or login failed
    """
    # Resolve SMTP server
    try:
        socket.gethostbyname(smtp_host)
    except Exception:
        raise ValidationError(
            _('Could not resolve %(smtp_host)s'),
            code='invalid_host',
            params={'smtp_host': smtp_host}
        )

    # Try connecting and login
    try:
        kwargs = {
            'host': smtp_host,
            'port': smtp_port,
            'use_tls': use_tls,
            'username': username,
            'password': password,
        }
        smtp_server = get_connection('django.core.mail.backends.smtp.EmailBackend', fail_silently=False, **kwargs)
        smtp_server.open()
        smtp_server.close()
    except SMTPAuthenticationError:
        # Failed login
        raise ValidationError(
            _('Unable to login with provided username and password on the SMTP host'),
            code='invalid_credentials'
        )
    except Exception:
        # Failed connection
        raise ValidationError(
            _('Could not connect to %(smtp_host)s:%(smtp_port)s'),
            code='invalid_connection',
            params={'smtp_host': smtp_host, 'smtp_port': smtp_port}
        )


def email_auth_update(user):
    """
    Check if there is an email account for the user that needs a new password.
    """
    should_update = EmailAccount.objects.filter(
        is_deleted=False,
        auth_ok=False,
        tenant=user.tenant,
        user_group__pk=user.pk,
    ).exists()

    return should_update


def unread_emails(user):
    """
    Returns a list of unread e-mails.
    Limit results with bodies to 10.
    Limit total results to 30.
    """
    limit_list = 10
    limit_excerpt = 5
    unread_emails_list = []

    # Look up the last few unread e-mail messages for owned accounts
    ctype = ContentType.objects.get_for_model(EmailAccount)
    email_accounts = list(user.messages_accounts_owned.filter(polymorphic_ctype=ctype))
    email_messages = EmailMessage.objects.filter(
        folder_identifier=INBOX,
        account__in=email_accounts,
        is_seen=False,
    ).order_by('-sort_by_date')
    unread_count = email_messages.count()

    email_messages = email_messages[:limit_list]  # eval slice

    # show excerpt for limit_excerpt messages
    for email_message in email_messages[:limit_excerpt]:
        unread_emails_list.append({
            'id': email_message.pk,
            'from': email_message.from_name,
            'time': email_message.sent_date,
            'message_excerpt': truncatechars(email_message.textify().lstrip('&nbsp;\n\r\n '), 100),
        })

    if len(email_messages) > limit_excerpt:
        # for more messages up to limit_list don't show excerpt
        for email_message in email_messages[limit_excerpt:]:
            unread_emails_list.append({
                'id': email_message.pk,
                'from': email_message.from_name,
                'time': email_message.sent_date,
            })

    return {
        'count': unread_count,
        'count_more': unread_count - len(unread_emails_list),
        'object_list': unread_emails_list,
    }


def create_task_status(task_name, args=None, kwargs=None):
    sig = str(signature(task_name, args=args, kwargs=kwargs))  # args and kwargs required?

    # Set status to PENDING since it's not running yet
    init_status = PENDING

    # Check for timelimit
    annotations_for_task = resolve_annotations(task_name)
    timelimit = annotations_for_task.get('time_limit')

    # Determine when this task should expire
    utc_before = datetime.now(tzutc())
    expires_at = utc_before + timedelta(seconds=timelimit)

    status = TaskStatus.objects.create(
        status=init_status,
        signature=sig,
        expires_at=expires_at,
    )

    return status

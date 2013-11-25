import re
from types import FunctionType
from urllib import unquote

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart, get_connection
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Field
from django.db.models.query_utils import Q
from django.template import Context, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, TemplateSyntaxError
from django.template.loader import get_template_from_string
from django.template.loader_tags import BlockNode, ExtendsNode
from python_imap.server import IMAP

from lily.messaging.email.decorators import get_safe_template
from lily.tenant.middleware import get_current_user


_EMAIL_PARAMETER_DICT = {}
_EMAIL_PARAMETER_CHOICES = {}


def get_field_names(field):
    """
    Set the field name and the verbose field name depending on the type of field

    :param field: The field from which we want the name
    :return: The field name and the verbose field name
    """
    if isinstance(field, FunctionType):
        field_name = field.__name__
        field_verbose_name = field.__name__.replace('_', ' ')
    elif isinstance(field, Field):
        field_name = field.name
        field_verbose_name = field.verbose_name

    return field_name, field_verbose_name


def get_email_parameter_dict():
    """
    If there is no e-mail parameter dict yet, construct it and return it.
    The e-mail parameter dict consists of all posible variables for e-mail templates.

    This function returns parameters organized by variable name for easy parsing.

    """
    if not _EMAIL_PARAMETER_DICT:
        for model in models.get_models():
            if hasattr(model, 'email_template_parameters'):
                for field in model.email_template_parameters:
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
            if hasattr(model, 'email_template_parameters'):
                for field in model.email_template_parameters:
                    field_name, field_verbose_name = get_field_names(field)

                    if '%s' % model._meta.verbose_name.title() in _EMAIL_PARAMETER_CHOICES:
                        _EMAIL_PARAMETER_CHOICES.get('%s' % model._meta.verbose_name.title()).update({
                            '%s_%s' % (model._meta.verbose_name.lower(), field_name.lower()): field_verbose_name.title(),
                        })
                    else:
                        _EMAIL_PARAMETER_CHOICES.update({
                            '%s' % model._meta.verbose_name.title(): {
                                '%s_%s' % (model._meta.verbose_name.lower(), field.name.lower()): field_verbose_name.title(),
                            }
                        })

    return _EMAIL_PARAMETER_CHOICES


def get_folder_unread_count(folder, email_accounts=None):
    """
    Return the number of unread email messages in folder for given email accounts.
    """
    from lily.messaging.email.models import EmailAccount, EmailMessage  # prevent circular dependency
    if email_accounts is None:
        email_accounts = get_current_user().get_messages_accounts(EmailAccount)

    return EmailMessage.objects.filter(Q(folder_identifier=folder) | Q(folder_name=folder), account__in=email_accounts, is_seen=False).count()


class TemplateParser(object):
    """
    Parse template input and provide helper functions for further template handling.
    """
    def __init__(self, text):
        self.valid_parameters = []
        self.valid_blocks = []

        text = self._escape_text(text.encode('utf-8')).strip()
        safe_get_template_from_string = get_safe_template(tags=['now', 'templatetag', ])(get_template_from_string)

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

    def get_parts(self, default_part='html_part', parts=None):
        """
        Return the contents of specified parts, if no parts are available return the default part.

        :param default_part: which part is filled when no parts are defined.
        :param parts: override the default recognized parts.
        """
        parts = parts or ['name', 'description', 'subject', 'html_part', 'text_part', ]
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
            lookup = model.email_template_lookup

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


def get_attachment_upload_path(instance, filename):
    return settings.EMAIL_ATTACHMENT_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'message_id': instance.message_id,
        'filename': filename
    }


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
            image['src'] = reverse('email_proxy_view', kwargs={'pk': inline_attachment.pk, 'path': inline_attachment.attachment.name})

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


def get_remote_messages(account, folder_name, criteria=['ALL'], modifiers=['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']):
    """
    Fetch messages for page *page* in *folder* for *account*.
    """
    from lily.messaging.email.models import EmailMessage
    from lily.messaging.email.tasks import save_email_messages

    server = None
    try:
        host = account.provider.imap_host
        port = account.provider.imap_port
        ssl = account.provider.imap_ssl
        server = IMAP(host, port, ssl)
        server.login(account.username,  account.password)

        folder = server.get_folder(folder_name)

        known_uids_qs = EmailMessage.objects.filter(account=account, folder_name=folder.name_on_server)
        known_uids = set(known_uids_qs.values_list('uid', flat=True))

        folder_count, remote_uids = server.get_uids(folder, criteria)

        # Get the difference between local and server uids
        new_uids = list(set(remote_uids).difference(known_uids))

        if len(new_uids):
            # Retrieve modifiers_new for new_uids
            folder_messages = server.get_messages(new_uids, modifiers, folder)

            if len(folder_messages) > 0:
                save_email_messages(folder_messages, account, folder, new_messages=True)
    finally:
        if server:
            server.logout()


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
            del(attachment['Content-Type'])
            del(attachment['Content-Disposition'])
            attachment.add_header('Content-Disposition', 'inline', filename=filename)
            attachment.add_header('Content-Type', mimetype, name=filename)
            attachment.add_header('Content-ID', '<%s>' % filename)
        return attachment

import email
import textwrap

from bs4 import BeautifulSoup
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext as _
from django_fields.fields import EncryptedCharField
from python_imap.folder import DRAFTS, TRASH
from python_imap.utils import convert_html_to_text

from lily.messaging.models import Message, MessagesAccount
from lily.settings import EMAIL_TEMPLATE_ATTACHMENT_UPLOAD_TO
from lily.tenant.models import TenantMixin, NullableTenantMixin
from lily.utils.models import EmailAddress
from lily.messaging.email.utils import get_attachment_upload_path


class EmailProvider(NullableTenantMixin):
    """
    A provider contains the connection information for an account.
    """
    name = models.CharField(max_length=30, blank=True, null=True)  # named providers can be selected to pre-fill the form.
    imap_host = models.CharField(max_length=32)
    imap_port = models.PositiveIntegerField()
    imap_ssl = models.BooleanField(default=False)
    smtp_host = models.CharField(max_length=32)
    smtp_port = models.PositiveIntegerField()
    smtp_ssl = models.BooleanField(default=False)

    def __unicode__(self):
        return self.imap_host if self.name and len(self.name.strip()) == 0 else self.name or ''

    class Meta:
        verbose_name = _('e-mail provider')
        verbose_name_plural = _('e-mail providers')


NO_EMAILACCOUNT_AUTH, OK_EMAILACCOUNT_AUTH, UNKNOWN_EMAILACCOUNT_AUTH = range(3)
EMAILACCOUNT_AUTH_CHOICES = (
    (NO_EMAILACCOUNT_AUTH, _('No (working) credentials')),
    (OK_EMAILACCOUNT_AUTH, _('Working credentials')),
    (UNKNOWN_EMAILACCOUNT_AUTH, _('Credentials needs testing')),
)


class EmailAccount(MessagesAccount):
    """
    An e-mail account.
    """
    from_name = models.CharField(max_length=255)
    signature = models.TextField(blank=True, null=True)
    email = models.ForeignKey(EmailAddress, related_name='email', unique=True)
    username = EncryptedCharField(max_length=255, cipher='AES', block_type='MODE_CBC')
    password = EncryptedCharField(max_length=255, cipher='AES', block_type='MODE_CBC')
    auth_ok = models.IntegerField(choices=EMAILACCOUNT_AUTH_CHOICES, default=NO_EMAILACCOUNT_AUTH)
    provider = models.ForeignKey(EmailProvider, related_name='email_accounts')
    last_sync_date = models.DateTimeField(default=None, null=True)
    folders = JSONField()

    def __unicode__(self):
        if self.from_name:
            return '%s (%s)' % (self.from_name, self.email.email_address)
        return self.email

    class Meta:
        verbose_name = _('e-mail account')
        verbose_name_plural = _('e-mail accounts')
        ordering = ['email__email_address']


class EmailMessage(Message):
    """
    A single e-mail message.
    """
    uid = models.IntegerField()  # unique id on the server
    flags = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    body_text = models.TextField(blank=True, null=True)
    size = models.IntegerField(default=0, null=True)  # size in bytes
    folder_name = models.CharField(max_length=255)
    folder_identifier = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    is_private = models.BooleanField(default=False)
    account = models.ForeignKey(EmailAccount, related_name='messages')

    def get_list_item_template(self):
        """
        Return the template that must be used for history list rendering
        """
        return 'messaging/email/email_message_list_single_object.html'

    def has_attachments(self):
        return self.attachments.count() > 0

    def get_conversation(self):
        """
        Return the entire conversation this message is a part of.
        """
        messages = []
        message = self.headers.filter(name='In-Reply-To')
        while message is not None:
            messages.append(message)
            try:
                message_id = message.headers.filter(name='In-Reply-To')
                message = EmailMessage.objects.get(header__name='MSG-ID', header_value=message_id)
            except EmailMessage.DoesNotExist:
                message = None

        return messages

    def textify(self):
        """
        Return a plain text version of the html body, and optionally replace <br> tags with line breaks (\n).
        """
        return self.body_text or convert_html_to_text(self.body_html, keep_linebreaks=True)

    def htmlify(self):
        """
        Return a html version of the text body, and optionally replace line breaks (\n) with <br> tags.
        """
        if self.body_text:
            return self.body_text.replace('\n', '<br />')
        return None

    @property
    def indented_body(self):
        """
        Return an indented version of the body, preferably the html part, but in case that doesn't exist the text part.
        This indented version of the body can be used to reply or forward an e-mail message.
        """
        if self.body_html:
            # In case of html, wrap body in blockquote tag.
            soup = BeautifulSoup(self.body_html)
            if soup.html is None:
                soup = BeautifulSoup("""<html>%s</html>""" % self.body_html)  # haven't figured out yet how to do this elegantly..

            soup.html.wrap(soup.new_tag('blockquote', type='cite'))
            soup.html.unwrap()
            return soup.decode()
        elif self.body_text:
            # In case of plain text, prepend '>' to every line of body.
            indented_body = textwrap.wrap(self.body_text, 80)
            indented_body = ['> %s' % line for line in indented_body]
            return '<br />'.join(indented_body)
        else:
            return ''

    @property
    def subject(self):
        header = None

        if hasattr(self, '_subject_header'):
            header = self._subject_header
        else:
            try:
                header = self.headers.get(name='Subject')
            except MultipleObjectsReturned:
                header = self.headers.filter(name='Subject').reverse()[0]
            except ObjectDoesNotExist:
                header = ''
            self._subject_header = header.value if header else ''

        return self._subject_header

    def to_emails(self, include_names=True, include_self=False):
        headers = None
        if hasattr(self, '_to_headers'):
            headers = self._to_headers
        else:
            headers = self.headers.filter(name='To')
            self._to_headers = headers

        if headers:
            to_emails = []
            to_names = []
            own_email_address = self.account.email.email_address
            for header in headers:
                for address in email.utils.getaddresses(header.value.split(',')):
                    # The name is allowed to be empty, email address is not
                    if (include_self or (address[0] != own_email_address and address[1] != own_email_address)) and address[1]:
                        # If there is no name available, use the email address
                        if include_names:
                            to_names.append(address[0])
                        to_emails.append(address[1])
            if include_names:
                return zip(to_names, to_emails)
            else:
                return to_emails
        return u'<%s>' % _(u'No address')

    @property
    def to_combined(self):
        headers = None
        if hasattr(self, '_to_headers'):
            headers = self._to_headers
        else:
            headers = self.headers.filter(name='To')
            self._to_headers = headers
        if headers:
            to = []
            for header in headers[0].value.split(','):
                parts = email.utils.parseaddr(header)
                if len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
                    to.append(u'"%s" <%s>' % (parts[0], parts[1]))
                elif len(parts[1]) > 0:
                    to.append(u'%s' % parts[1])
                elif len(parts[0]) > 0:
                    to.append(u'"%s"' % parts[0])

            return u', '.join(to)
        return u''

    @property
    def to_cc_combined(self):
        headers = None
        if hasattr(self, '_to_cc_headers'):
            headers = self._to_cc_headers
        else:
            headers = self.headers.filter(name='Cc')
            self._to_cc_headers = headers
        if headers:
            to_cc = []
            for header in headers[0].value.split(','):
                parts = email.utils.parseaddr(header)
                if len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
                    to_cc.append(u'"%s" <%s>' % (parts[0], parts[1]))
                elif len(parts[1]) > 0:
                    to_cc.append(u'%s' % parts[1])
                elif len(parts[0]) > 0:
                    to_cc.append(u'"%s"' % parts[0])

            return u', '.join(to_cc)
        return u''

    @property
    def to_bcc_combined(self):
        headers = None
        if hasattr(self, '_to_bcc_headers'):
            headers = self._to_bcc_headers
        else:
            headers = self.headers.filter(name='Bcc')
            self._to_bcc_headers = headers
        if headers:
            to_bcc = []
            for header in headers[0].value.split(','):
                parts = email.utils.parseaddr(header)
                if len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
                    to_bcc.append(u'"%s" <%s>' % (parts[0], parts[1]))
                elif len(parts[1]) > 0:
                    to_bcc.append(u'%s' % parts[1])
                elif len(parts[0]) > 0:
                    to_bcc.append(u'"%s"' % parts[0])

            return u', '.join(to_bcc)
        return u''

    @property
    def from_combined(self):
        header = None
        if hasattr(self, '_from_header'):
            header = self._from_header
        else:
            header = self.headers.filter(name='From')
            self._from_header = header
        if header:
            parts = email.utils.parseaddr(header[0].value)
            if len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
                from_combi = '"%s" <%s>' % (parts[0], parts[1])
            elif len(parts[1]) > 0:
                from_combi = '%s' % parts[1]
            else:
                from_combi = '"%s"' % parts[0]

            return from_combi
        return u''

    @property
    def from_name(self):
        header = None
        if hasattr(self, '_from_header'):
            header = self._from_header
        else:
            header = self.headers.filter(name='From')
            self._from_header = header
        if header:
            return email.utils.parseaddr(header[0].value)[0]
        return u''

    @property
    def from_email(self):
        header = None
        if hasattr(self, '_from_header'):
            header = self._from_header
        else:
            header = self.headers.filter(name='From')
            self._from_header = header
        if header:
            return email.utils.parseaddr(header[0].value)[1]
        return u'<%s>' % _(u'No address')

    @property
    def is_plain(self):
        header = self.headers.filter(name='Content-Type')
        if header:
            return header[0].value.startswith('text/plain')
        return False

    @property
    def is_draft(self):
        return DRAFTS in self.flags or self.folder_identifier == DRAFTS

    @property
    def is_deleted(self):
        return TRASH in self.flags

    def __unicode__(self):
        return u'%s - %s'.strip() % (email.utils.parseaddr(self.from_email), truncatechars(self.subject, 130))

    class Meta:
        verbose_name = _('e-mail message')
        verbose_name_plural = _('e-mail messages')
        unique_together = ('uid', 'folder_name', 'account')


class EmailAttachment(TenantMixin):
    """
    A single attachment linked to an e-mail message.
    """
    inline = models.BooleanField(default=False)
    attachment = models.FileField(upload_to=get_attachment_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    message = models.ForeignKey(EmailMessage, related_name='attachments')

    def __unicode__(self):
        return self.attachment.name

    class Meta:
        verbose_name = _('e-mail attachment')
        verbose_name_plural = _('e-mail attachments')


class EmailHeader(models.Model):
    """
    A single e-mail header linked to an e-mail message.
    Most common are: 'to', 'from' and 'content-type'.
    """
    name = models.CharField(max_length=255, db_index=True)
    value = models.TextField(null=True)
    message = models.ForeignKey(EmailMessage, related_name='headers')

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.value)


class EmailAddressHeader(models.Model):
    """
    A simplified header with just the name of the header and the email address from the value of the header.
    """
    name = models.CharField(max_length=255, db_index=True)
    value = models.TextField(null=True, db_index=True)
    message = models.ForeignKey(EmailMessage)

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.value)


class EmailLabel(models.Model):
    """
    A single label in which an e-mail message can be linked to.
    """
    name = models.CharField(max_length=50)
    message = models.ForeignKey(EmailMessage, related_name='labels')


class ActionStep(TenantMixin):
    """
    ActionStep helping decide the order in which to process e-mail messages.
    """
    LOW, NORMAL, HIGH = range(3)
    ACTION_STEP_PRIO = (
        (LOW, _('Low priority')),
        (NORMAL, _('Normal priority')),
        (HIGH, _('High priority'))
    )
    priority = models.IntegerField()
    done = models.BooleanField(default=False)
    message = models.ForeignKey(EmailMessage)


class EmailTemplate(TenantMixin, TimeStampedModel):
    """
    Emails can be composed using templates.
    A template is a predefined email in which parameters can be dynamically inserted.

    @name: name that is used to display templates in a list
    @description: what is this template handy for?
    @subject: default subject for the e-mail using this template
    @body_html: html part of the e-mail

    """
    name = models.CharField(verbose_name=_('template name'), max_length=255)
    description = models.TextField(verbose_name=_('template description'), blank=True)
    subject = models.CharField(verbose_name=_('message subject'), max_length=255, blank=True)
    body_html = models.TextField(verbose_name=_('html part'), blank=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')


class EmailTemplateAttachment(models.Model):
    """
    Default attachments that are added to templates.

    @template: foreign key to the template model
    @attachment: the actual file to add per default to all e-mails using the template

    """
    template = models.ForeignKey(EmailTemplate, verbose_name=_(''), related_name='attachments')
    attachment = models.FileField(verbose_name=_('template attachment'), upload_to=EMAIL_TEMPLATE_ATTACHMENT_UPLOAD_TO)

    def __unicode__(self):
        return u'%s: %s' % (_('attachment of'), self.template)

    class Meta:
        verbose_name = _('e-mail template attachment')
        verbose_name_plural = _('e-mail template attachments')


class EmailDraft(TimeStampedModel):
    send_from = models.ForeignKey(EmailAccount, verbose_name=_('From'), related_name='drafts')  # or simple charfield with modelchoices?
    send_to_normal = models.TextField(null=True, blank=True, verbose_name=_('To'))
    send_to_cc = models.TextField(null=True, blank=True, verbose_name=_('Cc'))
    send_to_bcc = models.TextField(null=True, blank=True, verbose_name=_('Bcc'))
    subject = models.CharField(null=True, blank=True, max_length=255, verbose_name=_('Subject'))
    body_html = models.TextField(null=True, blank=True, verbose_name=_('Html body'))

    def __unicode__(self):
        return u'%s - %s' % (self.send_from, self.subject)

    class Meta:
        verbose_name = _('e-mail draft')
        verbose_name_plural = _('e-mail drafts')


@receiver(post_delete, sender=EmailAttachment)
def post_delete_mail_attachment_handler(sender, **kwargs):
    attachment = kwargs['instance']
    storage, filename = attachment.attachment.storage, attachment.attachment.name
    storage.delete(filename)

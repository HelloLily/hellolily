import email
import textwrap

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext as _
from django_fields.fields import EncryptedCharField
from python_imap.folder import DRAFTS
from python_imap.utils import convert_html_to_text

from lily.messaging.models import Message, MessagesAccount
from lily.tenant.models import TenantMixin, NullableTenantMixin


def get_attachment_upload_path(instance, filename):
    if isinstance(instance, EmailOutboxAttachment):
        message_id = instance.email_outbox_message_id
    else:
        message_id = instance.message_id

    return settings.EMAIL_ATTACHMENT_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'message_id': message_id,
        'filename': filename
    }


def get_template_attachment_upload_path(instance, filename):
    return settings.EMAIL_TEMPLATE_ATTACHMENT_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'template_id': instance.template_id,
        'filename': filename
    }


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
        app_label = 'email'
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
    from_name = models.CharField(max_length=255, help_text=_('The sender\'s name your recipients see.'))
    label = models.CharField(max_length=255, blank=True, help_text=_('Give your account a custom name (optional).'))
    email = models.EmailField(max_length=255, help_text=_('The email address, used to identify you.'))
    username = EncryptedCharField(max_length=255, cipher='AES', block_type='MODE_CBC')
    password = EncryptedCharField(max_length=255, cipher='AES', block_type='MODE_CBC')
    auth_ok = models.IntegerField(choices=EMAILACCOUNT_AUTH_CHOICES, default=UNKNOWN_EMAILACCOUNT_AUTH)
    provider = models.ForeignKey(EmailProvider, related_name='email_accounts')
    last_sync_date = models.DateTimeField(default=None, null=True)
    folders = JSONField()

    def __unicode__(self):
        return self.label or self.email

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail account')
        verbose_name_plural = _('e-mail accounts')
        ordering = ['email']


class EmailMessage(Message):
    """
    A single e-mail message.
    """
    uid = models.IntegerField()  # unique id on the server
    flags = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    body_text = models.TextField(blank=True, null=True)
    size = models.IntegerField(default=0, null=True)  # size in bytes
    folder_name = models.CharField(max_length=255, db_index=True)
    folder_identifier = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    is_private = models.BooleanField(default=False)
    account = models.ForeignKey(EmailAccount, related_name='messages')
    sent_from_account = models.BooleanField(default=False)
    message_identifier = models.CharField(max_length=255)  # Message-ID header
    is_deleted = models.BooleanField(default=False, db_index=True)

    def get_list_item_template(self):
        """
        Return the template that must be used for history list rendering
        """
        return 'email/emailmessage_historylistitem.html'

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

    def get_email_operation_icon(self):
        """
        Return an icon which corresponds to the operation (sent, forward, reply, reply all) of the email
        """
        if not hasattr(self, '_in_reply_to_headers'):
            self._in_reply_to_headers = self.headers.filter(name__iexact='In-Reply-To')

        from_email = self.from_email
        operation = None

        # If this header is present, it's a reply to another email
        if self._in_reply_to_headers.exists():
            subject = self.subject
            # Check if it's a forwarded email
            if subject.lower().startswith('fwd:'):
                operation = 'forward'
            else:
                # Check if this reply is sent to a single or multiple recipients
                to_emails = self.to_emails(include_names=False)
                to_cc = self.to_cc_combined

                if len(to_emails) == 1 and not to_cc:
                    operation = 'reply'
                elif len(to_emails) > 1 or to_cc:
                    operation = 'reply-all'
        elif from_email == self.account.email:
            # If the sender is the user's email it's just a sent email
            operation = 'sent'

        return {
            'forward': 'icon-share-alt',  # TODO: Temp icon, change to fa-share once we upgrade to FontAwesome 4
            'reply': 'icon-reply',
            'reply-all': 'icon-reply-all',
            'sent': 'icon-location-arrow',  # TODO: Temp icon, change to fa-paper-plane once we upgrade to FontAwesome 4
        }.get(operation)

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
    def reply_body(self):
        """
        Return an version of the body which is used for replies or forwards.
        This is preferably the html part, but in case that doesn't exist we use the text part
        """
        if self.body_html:
            body_html = '<br /><br /><hr />' + self.body_html
            # In case of html, wrap body in blockquote tag.
            soup = BeautifulSoup(body_html)
            if soup.html is None:
                soup = BeautifulSoup("""<html>%s</html>""" % body_html)  # haven't figured out yet how to do this elegantly..

            soup.html.unwrap()
            return soup.decode()
        elif self.body_text:
            # In case of plain text, prepend '>' to every line of body.
            reply_body = textwrap.wrap(self.body_text, 80)
            reply_body = ['> %s' % line for line in reply_body]
            return '<br /><br />' + '<br />'.join(reply_body)
        else:
            return ''

    @property
    def subject(self):
        if hasattr(self, '_subject_header'):
            header = self._subject_header
        else:
            try:
                header = self.headers.get(name='Subject')
            except MultipleObjectsReturned:
                header = self.headers.filter(name='Subject').first()
            except ObjectDoesNotExist:
                header = ''
            self._subject_header = header.value if header else ''

        return self._subject_header

    def to_emails(self, include_names=True, include_self=False):
        if hasattr(self, '_to_headers'):
            headers = self._to_headers
        else:
            # For some reason certain headers are in the database twice, so get unique headers
            headers = self.headers.filter(name='To').order_by('name').distinct('name')
            self._to_headers = headers

        if headers:
            to_emails = []
            to_names = []
            own_email_address = self.account.email
            for header in headers:
                for address in email.utils.getaddresses(header.value.split(',')):
                    # The name is allowed to be empty, email address is not
                    if (include_self or (address[0] != own_email_address and address[1] != own_email_address)) and address[1]:
                        # If there's no name available, use the email address
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
    def from_combined(self):
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
    def is_readable(self):
        """
        Boolean set to True if emailmessage is in db or should be fetchable from IMAP.
        """
        if self.body_html is None or not self.body_html.strip() and (self.body_text is None or not self.body_text.strip()):
            if not self.account.is_deleted:
                return self.account.auth_ok is OK_EMAILACCOUNT_AUTH
        return True

    def __unicode__(self):
        return u'%s - %s'.strip() % (email.utils.parseaddr(self.from_email), truncatechars(self.subject, 130))

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail message')
        verbose_name_plural = _('e-mail messages')
        unique_together = ('uid', 'folder_name', 'account')
        index_together = [
            ['folder_name', 'account'],
        ]


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
        app_label = 'email'
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

    class Meta:
        app_label = 'email'


class EmailAddress(models.Model):
    email_address = models.CharField(max_length=1000, db_index=True)

    class Meta:
        app_label = 'email'


class EmailAddressHeader(TenantMixin):
    """
    A simplified header with just the name of the header and the email address from the value of the header.
    """
    name = models.CharField(max_length=255, db_index=True)
    value = models.TextField(null=True, db_index=True)
    email_address = models.ForeignKey(EmailAddress, null=True)
    message = models.ForeignKey(EmailMessage)
    sent_date = models.DateTimeField(null=True, db_index=True)
    message_identifier = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.value)

    class Meta:
        app_label = 'email'


class EmailLabel(models.Model):
    """
    A single label in which an e-mail message can be linked to.
    """
    name = models.CharField(max_length=50)
    message = models.ForeignKey(EmailMessage, related_name='labels')

    class Meta:
        app_label = 'email'


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

    class Meta:
        app_label = 'email'


class EmailTemplate(TenantMixin, TimeStampedModel):
    """
    Emails can be composed using templates.
    A template is a predefined email in which parameters can be dynamically inserted.

    @name: name that is used to display templates in a list
    @subject: default subject for the e-mail using this template
    @body_html: html part of the e-mail

    """
    name = models.CharField(verbose_name=_('template name'), max_length=255)
    subject = models.CharField(verbose_name=_('message subject'), max_length=255, blank=True)
    body_html = models.TextField(verbose_name=_('html part'), blank=True)
    default_for = models.ManyToManyField(EmailAccount, through='DefaultEmailTemplate')

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')


class DefaultEmailTemplate(models.Model):
    """
    Define a default template for a user.
    """
    user = models.ForeignKey('users.LilyUser', related_name='default_templates')
    template = models.ForeignKey(EmailTemplate, related_name='default_templates')
    account = models.ForeignKey(EmailAccount, related_name='default_templates')

    def __unicode__(self):
        return u'%s - %s' % (self.account, self.template)

    class Meta:
        app_label = 'email'
        verbose_name = _('default e-mail template')
        verbose_name_plural = _('default e-mail templates')
        unique_together = ('user', 'account')


class EmailTemplateAttachment(TenantMixin):
    """
    Default attachments that are added to templates.

    @template: foreign key to the template model
    @attachment: the actual file to add per default to all e-mails using the template

    """
    template = models.ForeignKey(EmailTemplate, verbose_name=_(''), related_name='attachments')
    attachment = models.FileField(verbose_name=_('template attachment'), upload_to=get_template_attachment_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=255, verbose_name=_('content type'))

    def save(self):
        if isinstance(self.attachment.file, (TemporaryUploadedFile, InMemoryUploadedFile)):
            # FieldFile object doesn't have the content_type attribute, so only set it if we're uploading new files
            self.content_type = self.attachment.file.content_type
            self.size = self.attachment.file.size

        super(EmailTemplateAttachment, self).save()

    def __unicode__(self):
        return u'%s: %s' % (_('attachment of'), self.template)

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail template attachment')
        verbose_name_plural = _('e-mail template attachments')


class EmailDraft(TimeStampedModel):
    send_from = models.ForeignKey(EmailAccount, verbose_name=_('From'), related_name='drafts')  # or simple charfield with modelchoices?
    send_to_normal = models.TextField(null=True, blank=True, verbose_name=_('to'))
    send_to_cc = models.TextField(null=True, blank=True, verbose_name=_('cc'))
    send_to_bcc = models.TextField(null=True, blank=True, verbose_name=_('bcc'))
    subject = models.CharField(null=True, blank=True, max_length=255, verbose_name=_('subject'))
    body_html = models.TextField(null=True, blank=True, verbose_name=_('html body'))

    def __unicode__(self):
        return u'%s - %s' % (self.send_from, self.subject)

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail draft')
        verbose_name_plural = _('e-mail drafts')


class EmailOutboxMessage(TenantMixin, models.Model):
    subject = models.CharField(null=True, blank=True, max_length=255, verbose_name=_('subject'))
    send_from = models.ForeignKey(EmailAccount, verbose_name=_('From'), related_name='outbox_messages')
    to = models.TextField(verbose_name=_('To'))
    cc = models.TextField(null=True, blank=True, verbose_name=_('cc'))
    bcc = models.TextField(null=True, blank=True, verbose_name=_('bcc'))
    body = models.TextField(null=True, blank=True, verbose_name=_('html body'))
    headers = models.TextField(null=True, blank=True, verbose_name=_('email headers'))
    mapped_attachments = models.IntegerField(verbose_name=_('number of mapped attachments'))

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail outbox message')
        verbose_name_plural = _('e-mail outbox messages')


class EmailOutboxAttachment(TenantMixin):
    inline = models.BooleanField(default=False)
    attachment = models.FileField(upload_to=get_attachment_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=255, verbose_name=_('content type'))
    email_outbox_message = models.ForeignKey(EmailOutboxMessage, related_name='attachments')

    def __unicode__(self):
        return self.attachment.name

    class Meta:
        app_label = 'email'
        verbose_name = _('e-mail outbox attachment')
        verbose_name_plural = _('e-mail outbox attachments')


@receiver(post_delete, sender=EmailAttachment)
def post_delete_mail_attachment_handler(sender, **kwargs):
    attachment = kwargs['instance']
    storage, filename = attachment.attachment.storage, attachment.attachment.name
    storage.delete(filename)

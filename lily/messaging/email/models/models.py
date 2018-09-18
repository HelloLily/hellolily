import anyjson
import mimetypes
import textwrap
import logging
import os

from email.header import Header
from email import Encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import parseaddr

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.storage import default_storage
from django.core.mail import SafeMIMEText, SafeMIMEMultipart, EmailMultiAlternatives
from django.urls import reverse
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import CredentialsField

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser
from lily.utils.models.mixins import DeletedMixin, TimeStampedModel

from ..sanitize import sanitize_html_email


logger = logging.getLogger(__name__)


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


def get_outbox_attachment_upload_path(instance, filename):
    return settings.EMAIL_ATTACHMENT_UPLOAD_TO % {
        'tenant_id': instance.tenant_id,
        'message_id': instance.email_outbox_message_id,
        'filename': filename
    }


def add_attachments_to_email(email, email_message, inline_headers):
    """ Retrieves all the attachments and adds them to the email. """
    from ..utils import get_attachment_filename_from_url
    for attachment in email.attachments.all():
        if attachment.inline:
            continue

        try:
            storage_file = default_storage._open(attachment.attachment.name)
        except IOError:
            logger.exception(
                'Couldn\'t get attachment, not sending {}:{}'.format(
                    email._meta.db_table,
                    email.id
                )
            )
            raise

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

        email_message.attach(msg)

    # Add the inline attachments to email message header
    for inline_header in inline_headers:
        main_type, sub_type = inline_header['content-type'].split('/', 1)
        if main_type == 'image':
            msg = MIMEImage(
                inline_header['content'],
                _subtype=sub_type,
                name=os.path.basename(inline_header['content-filename'])
            )
            msg.add_header(
                'Content-Disposition',
                inline_header['content-disposition'],
                filename=os.path.basename(inline_header['content-filename'])
            )
            msg.add_header('Content-ID', inline_header['content-id'])

            email_message.attach(msg)

    return True


class EmailAccount(TenantMixin, DeletedMixin):
    """
    Email account linked to a user.
    """
    PUBLIC, READ_ONLY, METADATA, PRIVATE = range(4)
    PRIVACY_CHOICES = (
        (PUBLIC, _('Group inbox')),
        (READ_ONLY, _('Public personal inbox')),
        (METADATA, _('Personal inbox, with shared metadata')),
        (PRIVATE, _('Private inbox')),
    )

    email_address = models.EmailField(max_length=254)
    from_name = models.CharField(max_length=254, default='')
    label = models.CharField(max_length=254, default='')
    is_authorized = models.BooleanField(default=False)

    # History id is a field to keep track of the sync status of a gmail box.
    history_id = models.BigIntegerField(null=True)
    temp_history_id = models.BigIntegerField(null=True)
    is_syncing = models.BooleanField(default=False)
    sync_failure_count = models.PositiveSmallIntegerField(default=0)
    only_new = models.NullBooleanField(default=False)

    owner = models.ForeignKey(LilyUser, related_name='email_accounts_owned')
    shared_with_users = models.ManyToManyField(
        LilyUser,
        related_name='shared_email_accounts',
        help_text=_('Select the users wich to share the account with.'),
        blank=True,
    )
    privacy = models.IntegerField(choices=PRIVACY_CHOICES, default=READ_ONLY)
    previous_privacy = models.IntegerField(choices=PRIVACY_CHOICES, null=True)
    is_active = models.BooleanField(default=True)

    color = models.CharField(max_length=7, blank=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.label, self.email_address)

    @property
    def is_public(self):
        return self.privacy == EmailAccount.PUBLIC

    @property
    def full_sync_needed(self):
        # Return if a full sync is needed on the account if it's newly added (history id missing) or it failed with a
        # history sync except when it is busy syncing already.
        return (not self.history_id or self.sync_failure_count > 0) and not self.is_syncing

    def to_header(self):
        """ Adds an extra header if from_name is set. Otherwise simply return email. """
        if self.from_name:
            return '"%s" <%s>' % (
                Header(u'%s' % self.from_name, 'utf-8'),
                self.email_address
            )
        return self.email_address

    class Meta:
        app_label = 'email'


class SharedEmailConfig(TenantMixin):
    """
    Settings that a user can set on email accounts shared with this user.
    """
    email_account = models.ForeignKey(EmailAccount)
    user = models.ForeignKey(LilyUser)
    is_hidden = models.BooleanField(default=False)
    privacy = models.IntegerField(choices=EmailAccount.PRIVACY_CHOICES, default=EmailAccount.PUBLIC)

    class Meta:
        app_label = 'email'
        unique_together = ('tenant', 'email_account', 'user')


class GmailCredentialsModel(models.Model):
    """
    OAuth2 credentials for Gmail API.
    """
    id = models.OneToOneField(EmailAccount, primary_key=True)
    credentials = CredentialsField()

    class Meta:
        app_label = 'email'


class EmailLabel(models.Model):
    """
    Label for EmailAccount and EmailMessage.
    """
    LABEL_SYSTEM, LABEL_USER = range(2)
    LABEL_TYPES = (
        (LABEL_SYSTEM, _('System')),
        (LABEL_USER, _('User')),
    )

    account = models.ForeignKey(EmailAccount, related_name='labels')
    label_type = models.IntegerField(choices=LABEL_TYPES, default=LABEL_SYSTEM)
    label_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    unread = models.PositiveIntegerField(default=0)  # Number of unread email messages with this label.

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'email'
        unique_together = ('account', 'label_id')


class Recipient(models.Model):
    """
    Name and email address of a recipient.
    """
    name = models.CharField(max_length=1000, null=True)
    email_address = models.CharField(max_length=1000, null=True, db_index=True)

    def __unicode__(self):
        return u'%s <%s>' % (self.name, self.email_address)

    class Meta:
        app_label = 'email'
        unique_together = ('name', 'email_address')


class EmailMessage(models.Model):
    """
    EmailMessage has all information from an email message.
    """
    NORMAL, REPLY, REPLY_ALL, FORWARD, FORWARD_MULTI = range(5)
    MESSAGE_TYPES = (
        (NORMAL, _('Email message')),
        (REPLY, _('Reply email message')),
        (REPLY_ALL, _('Reply-all email message')),
        (FORWARD, _('Forward email message')),
        (FORWARD_MULTI, _('Forward-multi email message')),
    )

    account = models.ForeignKey(EmailAccount, related_name='messages')
    body_html = models.TextField(default='')
    body_text = models.TextField(default='')
    draft_id = models.CharField(max_length=50, db_index=True, default='')
    has_attachment = models.BooleanField(default=False)
    labels = models.ManyToManyField(EmailLabel, related_name='messages')
    message_id = models.CharField(max_length=50, db_index=True)
    read = models.BooleanField(default=False, db_index=True)
    received_by = models.ManyToManyField(Recipient, related_name='received_messages')
    received_by_cc = models.ManyToManyField(Recipient, related_name='received_messages_as_cc')
    received_by_bcc = models.ManyToManyField(Recipient, related_name='received_messages_as_bcc')
    sender = models.ForeignKey(Recipient, related_name='sent_messages')
    sent_date = models.DateTimeField(db_index=True)
    snippet = models.TextField(default='')
    subject = models.TextField(default='')
    thread_id = models.CharField(max_length=50, db_index=True)
    is_inbox_message = models.NullBooleanField(_('Is inbox'), db_index=True)
    is_trashed_message = models.NullBooleanField(_('Is trashed'), db_index=True)
    is_spam_message = models.NullBooleanField(_('Is spam'), db_index=True)
    is_sent_message = models.NullBooleanField(_('Is sent'), db_index=True)
    is_draft_message = models.NullBooleanField(_('Is draft'), db_index=True)
    is_starred_message = models.NullBooleanField(_('Is starred'), db_index=True)
    message_type = models.PositiveSmallIntegerField(choices=MESSAGE_TYPES, null=True, default=None)
    message_type_to_id = models.PositiveIntegerField(null=True, default=None)  # Id it is a reply to, or forward of.

    @property
    def tenant_id(self):
        return self.account.tenant_id

    @property
    def reply_body(self):
        from ..utils import create_a_beautiful_soup_object
        """
        Return a version of the body which is used for replies or forwards.
        This is preferably the html part, but in case that doesn't exist we use the plain text part.
        """
        if self.body_html:
            # In case of html, wrap body in blockquote tag.
            soup = create_a_beautiful_soup_object(self.body_html)

            if not soup.html:
                # Haven't figured out yet how to do this elegantly.
                html = '<html>%s</html>' % self.body_html
                soup = create_a_beautiful_soup_object(html)

            if not soup or soup.get_text == "":
                html = self.body_html
            else:
                soup.html.unwrap()
                html = soup.decode()

            html = sanitize_html_email(html)
            return html
        elif self.body_text:
            # In case of plain text, prepend '>' to every line of body.
            reply_body = []
            for line in self.body_text.splitlines():
                reply_body.extend(textwrap.wrap(line, 120))
            reply_body = ['> %s' % line for line in reply_body]
            return '<br /><br /><br />'.join(reply_body)
        else:
            return ''

    def fast_label_check(self, label_name):
        """
        Do a label check that checks if a field is prefetched, making it way
        faster for optimized queries.
        """
        if hasattr(self, '_prefetched_objects_cache') and 'labels' in self._prefetched_objects_cache:
            return label_name in [label.label_id for label in self.labels.all()]
        else:
            return self.labels.filter(label_id=label_name).exists()

    @property
    def is_trashed(self):
        # When the instance variable is present, don't evaluate the corresponding label.
        if hasattr(self, '_is_trashed'):
            return self._is_trashed
        else:
            return self.fast_label_check(settings.GMAIL_LABEL_TRASH)

    @property
    def is_starred(self):
        # When the instance variable is present, don't evaluate the corresponding label.
        if hasattr(self, '_is_starred'):
            return self._is_starred
        else:
            return self.fast_label_check(settings.GMAIL_LABEL_STAR)

    @property
    def is_draft(self):
        return self.fast_label_check(settings.GMAIL_LABEL_DRAFT)

    @property
    def is_important(self):
        return self.fast_label_check(settings.GMAIL_LABEL_IMPORTANT)

    @property
    def is_spam(self):
        # When the instance variable is present, don't evaluate the corresponding label.
        if hasattr(self, '_is_spam'):
            return self._is_spam
        else:
            return self.fast_label_check(settings.GMAIL_LABEL_SPAM)

    @property
    def is_archived(self):
        # When the instance variable is present, don't evaluate the corresponding label.
        if hasattr(self, '_is_archived'):
            return self._is_archived
        else:
            return not self.fast_label_check(settings.GMAIL_LABEL_INBOX)

    @property
    def is_deleted(self):
        return hasattr(self, '_is_deleted') and self._is_deleted

    def get_message_id(self):
        header = self.headers.filter(name__istartswith='message-id').first()
        if header:
            return header.value

    @property
    def reply_to(self):
        """
        Return the reply to address if it is present as a header, otherwise use email address of the sender.
        """
        header = self.headers.filter(name__istartswith='reply-to').first()
        if header:
            # A reply-to header can contain a plain email address, an email address enclosed by brackets,
            # or has a "name" <foo@bar.com> construction.
            # So return only the email address instead of the actual header value.
            return parseaddr(header.value)[1]
        else:
            return self.sender.email_address

    @property
    def content_type(self):
        """
        Return the content type (Django model) for this model
        """
        return ContentType.objects.get(app_label="email", model="emailmessage")

    def __unicode__(self):
        return u'%s: %s' % (self.sender, self.snippet)

    class Meta:
        app_label = 'email'
        unique_together = ('account', 'message_id')
        ordering = ['-sent_date']


class EmailHeader(models.Model):
    """
    Headers for an EmailMessage.
    """
    message = models.ForeignKey(EmailMessage, related_name='headers')
    name = models.CharField(max_length=100)
    value = models.TextField()

    def __unicode__(self):
        return u'%s: %s' % (self.name, self.value)

    class Meta:
        app_label = 'email'


class EmailAttachment(models.Model):
    """
    Email attachment for an EmailMessage.
    """
    attachment = models.FileField(upload_to=get_attachment_upload_path, max_length=255)
    cid = models.TextField(default='')
    inline = models.BooleanField(default=False)
    message = models.ForeignKey(EmailMessage, related_name='attachments')
    size = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.attachment.name.split('/')[-1]

    @property
    def name(self):
        return self.attachment.name.split('/')[-1]

    def download_url(self):
        return reverse('download', kwargs={
            'model_name': 'email',
            'field_name': 'attachment',
            'object_id': self.id,
        })

    class Meta:
        app_label = 'email'


class NoEmailMessageId(models.Model):
    """
    Place to store message_ids that are not an email.
    """
    account = models.ForeignKey(EmailAccount, related_name='no_messages')
    message_id = models.CharField(max_length=50, db_index=True)

    class Meta:
        app_label = 'email'


class EmailTemplateFolder(TenantMixin):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'email'


class EmailTemplate(TenantMixin, TimeStampedModel):
    """
    Emails can be composed using templates.
    A template is a predefined email in which parameters can be dynamically inserted.

    @name: name that is used to display templates in a list.
    @subject: default subject for the email using this template.
    @body_html: html part of the email.

    """
    name = models.CharField(verbose_name=_('template name'), max_length=255)
    subject = models.CharField(verbose_name=_('message subject'), max_length=255, blank=True)
    body_html = models.TextField(verbose_name=_('html part'), blank=True)
    default_for = models.ManyToManyField(EmailAccount, through='DefaultEmailTemplate')
    folder = models.ForeignKey(EmailTemplateFolder, related_name='email_templates', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label = 'email'
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')


class TemplateVariable(TenantMixin):
    NO_YES_CHOICES = (
        (False, _('No')),
        (True, _('Yes')),
    )

    name = models.CharField(verbose_name=_('variable name'), max_length=255)
    text = models.TextField(verbose_name='variable text')
    owner = models.ForeignKey(LilyUser, related_name='template_variable')
    is_public = models.BooleanField(
        default=False,
        choices=NO_YES_CHOICES,
        help_text='A public template variable is available to everyone in your organisation'
    )

    class Meta:
        app_label = 'email'
        verbose_name = _('email template variable')
        verbose_name_plural = _('email template variables')


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
        verbose_name = _('default email template')
        verbose_name_plural = _('default email templates')
        unique_together = ('user', 'account')


class EmailTemplateAttachment(TenantMixin):
    """
    Default attachments that are added to templates.

    @template: foreign key to the template model
    @attachment: the actual file to add per default to all emails using the template
    """
    attachment = models.FileField(
        verbose_name=_('template attachment'),
        upload_to=get_template_attachment_upload_path,
        max_length=255
    )
    content_type = models.CharField(max_length=255, verbose_name=_('content type'))
    size = models.PositiveIntegerField(default=0)
    template = models.ForeignKey(EmailTemplate, verbose_name=_(''), related_name='attachments')

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
        verbose_name = _('email template attachment')
        verbose_name_plural = _('email template attachments')


class EmailOutboxMessage(TenantMixin, models.Model):
    """ Outbox email messages serve as an intermediary between Lily and Gmail.
    These are used to instruct Gmail about the email that has to be send.
    When this is model is sent it is replaced by an EmailMessage, which is
    recognized by both parties. """
    bcc = models.TextField(null=True, blank=True, verbose_name=_('bcc'))
    body = models.TextField(null=True, blank=True, verbose_name=_('html body'))
    cc = models.TextField(null=True, blank=True, verbose_name=_('cc'))
    headers = models.TextField(null=True, blank=True, verbose_name=_('email headers'))
    mapped_attachments = models.IntegerField(verbose_name=_('number of mapped attachments'))
    original_attachment_ids = models.TextField(default='', validators=[validate_comma_separated_integer_list])
    subject = models.CharField(null=True, blank=True, max_length=255, verbose_name=_('subject'))
    send_from = models.ForeignKey(EmailAccount, verbose_name=_('from'), related_name='outbox_messages')
    template_attachment_ids = models.CharField(
        max_length=255,
        default='',
        validators=[validate_comma_separated_integer_list]
    )
    to = models.TextField(verbose_name=_('to'))
    original_message_id = models.CharField(null=True, blank=True, max_length=50, db_index=True)

    def message(self):
        from ..utils import replace_cid_and_change_headers

        to = anyjson.loads(self.to)
        cc = anyjson.loads(self.cc)
        bcc = anyjson.loads(self.bcc)

        html, text, inline_headers = replace_cid_and_change_headers(self.body, self.original_message_id)

        email_message = SafeMIMEMultipart('related')
        email_message['Subject'] = self.subject
        email_message['From'] = self.send_from.to_header()

        if to:
            email_message['To'] = ','.join(list(to))
        if cc:
            email_message['cc'] = ','.join(list(cc))
        if bcc:
            email_message['bcc'] = ','.join(list(bcc))

        email_message_alternative = SafeMIMEMultipart('alternative')
        email_message.attach(email_message_alternative)

        email_message_text = SafeMIMEText(text, 'plain', 'utf-8')
        email_message_alternative.attach(email_message_text)

        email_message_html = SafeMIMEText(html, 'html', 'utf-8')
        email_message_alternative.attach(email_message_html)

        try:
            add_attachments_to_email(self, email_message, inline_headers)
        except IOError:
            return False

        return email_message

    class Meta:
        app_label = 'email'
        verbose_name = _('email outbox message')
        verbose_name_plural = _('email outbox messages')


class EmailOutboxAttachment(TenantMixin):
    inline = models.BooleanField(default=False)
    attachment = models.FileField(upload_to=get_outbox_attachment_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=255, verbose_name=_('content type'))
    email_outbox_message = models.ForeignKey(EmailOutboxMessage, related_name='attachments')

    def __unicode__(self):
        return self.attachment.name

    class Meta:
        app_label = 'email'
        verbose_name = _('email outbox attachment')
        verbose_name_plural = _('email outbox attachments')


@receiver(post_delete, sender=EmailAttachment)
def post_delete_mail_attachment_handler(sender, **kwargs):
    attachment = kwargs['instance']
    storage, filename = attachment.attachment.storage, attachment.attachment.name
    storage.delete(filename)


class EmailDraft(TenantMixin, models.Model):
    """ Almost-exact-replica of EmailOutboxMessage, the key difference here is
    that the to, cc and bcc fields are Arrayfields. """
    to = ArrayField(models.EmailField(max_length=254), verbose_name=_('to'))
    cc = ArrayField(models.EmailField(max_length=254), verbose_name=_('cc'))
    bcc = ArrayField(models.EmailField(max_length=254), verbose_name=_('bcc'))
    headers = JSONField(default=dict, verbose_name=_('email headers'))
    subject = models.CharField(blank=True, max_length=255, verbose_name=_('subject'))
    body = models.TextField(blank=True, verbose_name=_('html body'))
    mapped_attachments = models.IntegerField(verbose_name=_('number of mapped attachments'))
    original_attachment_ids = models.TextField(default='', validators=[validate_comma_separated_integer_list])
    send_from = models.ForeignKey(EmailAccount, verbose_name=_('from'), related_name='draft_messages')
    template_attachment_ids = models.CharField(
        max_length=255,
        default='',
        validators=[validate_comma_separated_integer_list]
    )
    original_message_id = models.CharField(default='', blank=True, max_length=50, db_index=True)

    def mime_message(self):
        from ..utils import replace_cid_and_change_headers

        html, text, inline_headers = replace_cid_and_change_headers(
            self.body,
            self.original_message_id
        )

        email = EmailMultiAlternatives(
            self.subject,
            text,  # stripped from html
            self.send_from.to_header(),
            to=self.to,
            bcc=self.bcc,
            headers={}
        )

        email.attach_alternative(html, mimetype='text/html')
        email_message = email.message()

        try:
            add_attachments_to_email(self, email_message, inline_headers)
        except IOError:
            raise

        return email_message

    class Meta:
        app_label = 'email'
        verbose_name = _('email draft message')
        verbose_name_plural = _('email draft messages')


class EmailDraftAttachment(TenantMixin):
    inline = models.BooleanField(default=False)
    attachment = models.FileField(upload_to=get_outbox_attachment_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=255, verbose_name=_('content type'))
    email_draft = models.ForeignKey(EmailDraft, related_name='attachments')

    def __unicode__(self):
        return self.attachment.name

    class Meta:
        app_label = 'email'
        verbose_name = _('email draft attachment')
        verbose_name_plural = _('email draft attachments')

import anyjson
from bs4 import BeautifulSoup
from email.header import Header
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import logging
import mimetypes
import os
import textwrap
import traceback

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from oauth2client.django_orm import CredentialsField
from python_imap.utils import convert_html_to_text

from lily.tenant.models import TenantMixin
from lily.users.models import LilyUser
from lily.utils.models.mixins import DeletedMixin


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


class EmailAccount(TenantMixin, DeletedMixin):
    """
    Email Account linked to a user
    """
    email_address = models.EmailField(max_length=254)
    from_name = models.CharField(max_length=254, default='')
    label = models.CharField(max_length=254, default='')
    is_authorized = models.BooleanField(default=False)

    # History id is a field to keep track of the sync status of a gmail box
    history_id = models.BigIntegerField(null=True)
    temp_history_id = models.BigIntegerField(null=True)

    owner = models.ForeignKey(LilyUser, related_name='email_accounts_owned')
    shared_with_users = models.ManyToManyField(
        LilyUser,
        related_name='shared_email_accounts',
        help_text=_('Select the users wich to share the account with.'),
        blank=True,
    )
    public = models.BooleanField(default=False, help_text=_('Make the email account accessible for the whole company.'))

    def __unicode__(self):
        return u'%s  (%s)' % (self.label, self.email_address)

    def is_owned_by_user(self):
        return True

    class Meta:
        app_label = 'email'


class GmailCredentialsModel(models.Model):
    """
    OAuth2 credentials for gmail api
    """
    id = models.ForeignKey(EmailAccount, primary_key=True)
    credentials = CredentialsField()

    class Meta:
        app_label = 'email'


class EmailLabel(models.Model):
    """
    Label for EmailAccount and EmailMessage
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
    unread = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'email'
        unique_together = ('account', 'label_id')


class Recipient(models.Model):
    """
    Name and email address of a recipient
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
    EmailMessage has all information from an email message
    """
    account = models.ForeignKey(EmailAccount, related_name='messages')
    labels = models.ManyToManyField(EmailLabel, related_name='messages')
    sender = models.ForeignKey(Recipient, related_name='sent_messages')
    received_by = models.ManyToManyField(Recipient, related_name='received_messages')
    received_by_cc = models.ManyToManyField(Recipient, related_name='received_messages_as_cc')
    message_id = models.CharField(max_length=50, db_index=True)
    thread_id = models.CharField(max_length=50, db_index=True)
    sent_date = models.DateTimeField(db_index=True)
    read = models.BooleanField(default=False, db_index=True)
    subject = models.TextField(default='')
    snippet = models.TextField(default='')
    has_attachment = models.BooleanField(default=False)
    body_html = models.TextField(default='')
    body_text = models.TextField(default='')

    @property
    def tenant_id(self):
        return self.account.tenant_id

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

    class Meta:
        app_label = 'email'
        unique_together = ('account', 'message_id')
        ordering = ['-sent_date']

    def __unicode__(self):
        return u'%s: %s' % (self.sender, self.snippet)


class EmailHeader(models.Model):
    """
    Headers for an EmailMessage
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
    Email attachment for an EmailMessage
    """
    inline = models.BooleanField(default=False)
    attachment = models.FileField(upload_to=get_attachment_upload_path, max_length=255)
    size = models.PositiveIntegerField(default=0)
    message = models.ForeignKey(EmailMessage, related_name='attachments')

    def __unicode__(self):
        return self.attachment.name

    class Meta:
        app_label = 'email'


class NoEmailMessageId(models.Model):
    """
    Place to store message_ids that are not an email
    """
    account = models.ForeignKey(EmailAccount, related_name='no_messages')
    message_id = models.CharField(max_length=50, db_index=True)

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
    send_from = models.ForeignKey(EmailAccount, verbose_name=_('from'), related_name='outbox_messages')
    to = models.TextField(verbose_name=_('to'))
    cc = models.TextField(null=True, blank=True, verbose_name=_('cc'))
    bcc = models.TextField(null=True, blank=True, verbose_name=_('bcc'))
    body = models.TextField(null=True, blank=True, verbose_name=_('html body'))
    headers = models.TextField(null=True, blank=True, verbose_name=_('email headers'))
    mapped_attachments = models.IntegerField(verbose_name=_('number of mapped attachments'))

    def message(self):
        from ..utils import EmailMultiRelated, get_attachment_filename_from_url

        to = anyjson.loads(self.to)
        cc = anyjson.loads(self.cc)
        bcc = anyjson.loads(self.bcc)

        if self.send_from.from_name:
            # Add account name to From header if one is available
            from_email = '"%s" <%s>' % (
                Header(u'%s' % self.send_from.from_name, 'utf-8'),
                self.send_from.email_address
            )
        else:
            # Otherwise only add the email address
            from_email = self.send_from.email_address

        message_data = dict(
            subject=self.subject,
            from_email=from_email,
            to=to,
            cc=cc,
            bcc=bcc,
            headers=anyjson.loads(self.headers),
            body=convert_html_to_text(self.body, keep_linebreaks=True),
        )

        if self.mapped_attachments != 0:
            # Attach an HTML version as alternative to *body*
            email_message = EmailMultiAlternatives(**message_data)
        else:
            # Use multipart/related when sending inline images
            email_message = EmailMultiRelated(**message_data)

        email_message.attach_alternative(self.body, 'text/html')

        attachments = self.attachments.all()

        for attachment in attachments:
            try:
                storage_file = default_storage._open(attachment.attachment.name)
            except IOError, e:
                logger.error(traceback.format_exc(e))
                return False

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

            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))

            email_message.attach(msg)

        return email_message.message()

    def message(self):
        from ..utils import EmailMultiRelated, get_attachment_filename_from_url

        to = anyjson.loads(self.to)
        cc = anyjson.loads(self.cc)
        bcc = anyjson.loads(self.bcc)

        if self.send_from.from_name:
            # Add account name to From header if one is available
            from_email = '"%s" <%s>' % (
                Header(u'%s' % self.send_from.from_name, 'utf-8'),
                self.send_from.email_address
            )
        else:
            # Otherwise only add the email address
            from_email = self.send_from.email_address

        message_data = dict(
            subject=self.subject,
            from_email=from_email,
            to=to,
            cc=cc,
            bcc=bcc,
            headers=anyjson.loads(self.headers),
            body=convert_html_to_text(self.body, keep_linebreaks=True),
        )

        if self.mapped_attachments != 0:
            # Attach an HTML version as alternative to *body*
            email_message = EmailMultiAlternatives(**message_data)
        else:
            # Use multipart/related when sending inline images
            email_message = EmailMultiRelated(**message_data)

        email_message.attach_alternative(self.body, 'text/html')

        attachments = self.attachments.all()

        for attachment in attachments:
            try:
                storage_file = default_storage._open(attachment.attachment.name)
            except IOError, e:
                logger.error(traceback.format_exc(e))
                return False

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

            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))

            email_message.attach(msg)

        return email_message.message()

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

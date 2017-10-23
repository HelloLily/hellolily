from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import CredentialsField

from email_wrapper_lib.conf import settings
from email_wrapper_lib.providers import registry

from .mixins import TimeStampMixin, SoftDeleteMixin


class EmailAccount(SoftDeleteMixin, TimeStampMixin, models.Model):
    NEW, IDLE, SYNCING, ERROR, RESYNC = range(5)
    ACCOUNT_STATUSES = (
        (NEW, _('new')),
        (IDLE, _('idle')),
        (SYNCING, _('syncing')),
        (ERROR, _('error')),
        (RESYNC, _('resync')),
    )

    # id = models.BigAutoField(
    #     primary_key=True
    # )
    username = models.CharField(
        verbose_name=_('Username'),
        unique=True,
        max_length=255
    )
    user_id = models.CharField(
        verbose_name=_('User id'),
        unique=True,
        max_length=255
    )
    credentials = CredentialsField()
    status = models.PositiveSmallIntegerField(
        verbose_name=_('Status'),
        choices=ACCOUNT_STATUSES,
        default=NEW,
        db_index=True
    )
    provider_id = models.PositiveSmallIntegerField(
        verbose_name=_('Provider id'),
        choices=registry.choices,
        db_index=True
    )
    subscription_id = models.CharField(
        verbose_name=_('Subscription id'),
        null=True,
        max_length=255
    )
    history_token = models.CharField(
        verbose_name=_('History token'),
        null=True,
        max_length=255
    )
    page_token = models.CharField(
        verbose_name=_('Page token'),
        null=True,
        max_length=255
    )

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailRecipient(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255
    )
    email_address = models.EmailField(
        verbose_name=_('Email')
    )
    raw_value = models.CharField(
        verbose_name=_('Raw value'),
        max_length=255,
        unique=True,
        db_index=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        self.raw_value = '{} <{}>'.format(self.name, self.email_address)
        super(EmailRecipient, self).save(*args, **kwargs)

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailFolder(models.Model):
    SYSTEM, USER = range(2)
    FOLDER_TYPES = (
        (SYSTEM, _('System')),
        (USER, _('User')),
    )

    account = models.ForeignKey(
        to='EmailAccount',
        on_delete=models.CASCADE,
        verbose_name=_('Account'),
        related_name='folders'
    )
    parent_id = models.CharField(
        verbose_name=_('Parent'),
        max_length=255,
        null=True
    )
    remote_id = models.CharField(
        verbose_name=_('Remote id'),
        max_length=255
    )
    remote_value = models.CharField(
        verbose_name=_('Remote value'),
        max_length=255
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255
    )
    folder_type = models.PositiveSmallIntegerField(
        verbose_name=_('Folder type'),
        choices=FOLDER_TYPES
    )
    unread_count = models.PositiveIntegerField(
        verbose_name=_('Unread count')
    )
    history_token = models.CharField(
        verbose_name=_('History token'),
        null=True,
        max_length=255
    )
    page_token = models.CharField(
        verbose_name=_('Page token'),
        null=True,
        max_length=255
    )

    class Meta:
        unique_together = ('account', 'remote_id', 'remote_value')
        app_label = 'email_wrapper_lib'


class EmailMessage(models.Model):
    # id = models.BigAutoField(
    #     primary_key=True
    # )
    remote_id = models.CharField(
        verbose_name=_('Remote id'),
        max_length=255
    )
    thread_id = models.CharField(
        verbose_name=_('Thread id'),
        max_length=255
    )
    message_id = models.CharField(
        verbose_name=_('Message id'),
        max_length=255
    )
    account = models.ForeignKey(
        to='EmailAccount',
        on_delete=models.CASCADE,
        verbose_name=_('Account'),
        related_name='messages'
    )
    folder = models.ManyToManyField(
        to='EmailFolder',
        verbose_name=_('Folder'),
        related_name='messages'
    )
    recipients = models.ManyToManyField(
        to='EmailRecipient',
        through='EmailMessageToEmailRecipient',
        verbose_name=_('Recipients'),
        related_name='messages'
    )
    snippet = models.CharField(
        verbose_name=_('Snippet'),
        max_length=255
    )
    subject = models.CharField(
        verbose_name=_('Subject'),
        max_length=255
    )
    # TODO: what the meaning of this date field? creation date of the message in our db, or remote "ReceivedDateTime"?
    date = models.DateTimeField(
        verbose_name=_('Date')
    )
    is_read = models.BooleanField(
        verbose_name=_('Is read')
    )
    is_starred = models.BooleanField(
        verbose_name=_('Is starred')
    )

    # Do we need the following? These are just labels and have no effect on how they are showed in the inbox and stuff?
    # is_draft = models.BooleanField(_('Is draft'))
    # is_important = models.BooleanField(_('Is important'))
    # is_archived = models.BooleanField(_('Is archived'))
    # is_trashed = models.BooleanField(_('Is trashed'))
    # is_spam = models.BooleanField(_('Is spam'))
    # is_sent = models.BooleanField(_('Is sent'))

    def get_recipients_by_type(self, recipient_type):
        if hasattr(self, '_recipient_type_{}'.format(recipient_type)):
            return getattr(self, '_recipient_type_{}'.format(recipient_type))
        elif hasattr(self, '_prefetched_objects_cache') and 'recipients' in self._prefetched_objects_cache:
            return [rec for rec in self.recipients.all() if rec.recipient_type == recipient_type]
        else:
            # TODO: Change query so results are cached.
            return list(self.recipients.filter(recipient_type=recipient_type))

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailMessageToEmailRecipient(models.Model):
    TO, CC, BCC, FROM, SENDER, REPLY_TO = range(6)
    RECIPIENT_TYPES = (
        (TO, _('To')),
        (CC, _('CC')),
        (BCC, _('BCC')),
        (FROM, _('From')),
        (SENDER, _('Sender')),
        (REPLY_TO, _('Reply to')),
    )

    message = models.ForeignKey(
        to='EmailMessage',
        on_delete=models.CASCADE,
        verbose_name=_('Message')
    )
    recipient = models.ForeignKey(
        to='EmailRecipient',
        on_delete=models.CASCADE,
        verbose_name=_('Recipient')
    )
    recipient_type = models.PositiveSmallIntegerField(
        verbose_name=_('Recipient type'),
        choices=RECIPIENT_TYPES
    )

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailDraft(models.Model):
    subject = models.CharField(
        max_length=255,
        verbose_name=_('Subject'),
        blank=True,
        default=''
    )
    body_text = models.TextField(
        verbose_name=_('Body text'),
        blank=True,
        default=''
    )
    body_html = models.TextField(
        verbose_name=_('Body html'),
        blank=True,
        default=''
    )
    recipients = models.ManyToManyField(
        to='EmailRecipient',
        through='EmailDraftToEmailRecipient',
        verbose_name=_('Recipients'),
        related_name='drafts'
    )
    account = models.ForeignKey(
        to='EmailAccount',
        on_delete=models.CASCADE,
        verbose_name=_('Account'),
        related_name='drafts',
    )
    in_reply_to = models.ForeignKey(
        to='EmailMessage',
        on_delete=models.SET_NULL,
        verbose_name=_('In reply to'),
        related_name='draft_replies',
        null=True
    )

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailDraftToEmailRecipient(models.Model):
    TO, CC, BCC = range(3)
    RECIPIENT_TYPES = (
        (TO, _('To')),
        (CC, _('CC')),
        (BCC, _('BCC')),
    )

    draft = models.ForeignKey(
        to='EmailDraft',
        on_delete=models.CASCADE,
        verbose_name=_('Draft')
    )
    recipient = models.ForeignKey(
        to='EmailRecipient',
        on_delete=models.CASCADE,
        verbose_name=_('Recipient')
    )
    recipient_type = models.PositiveSmallIntegerField(
        verbose_name=_('Recipient type'),
        choices=RECIPIENT_TYPES
    )

    class Meta:
        app_label = 'email_wrapper_lib'


def attachment_upload_path(instance, filename):
    return settings.ATTACHMENT_UPLOAD_PATH.format(
        draft_id=instance.draft_id,
        filename=filename
    )


class EmailDraftAttachment(models.Model):
    inline = models.BooleanField(
        default=False,
        verbose_name=_('Inline')
    )
    file = models.FileField(
        upload_to=attachment_upload_path,
        max_length=255,
        verbose_name=_('File')
    )
    # TODO: Add in email api.
    # size = models.PositiveIntegerField(
    #     default=0,
    #     verbose_name=_('Size')
    # )
    # content_type = models.CharField(
    #     max_length=255,
    #     verbose_name=_('Content type')
    # )
    draft = models.ForeignKey(
        to='EmailDraft',
        related_name='attachments'
    )

    def __unicode__(self):
        return self.file.name

    class Meta:
        app_label = 'email_wrapper_lib'
        verbose_name = _('email outbox attachment')
        verbose_name_plural = _('email outbox attachments')

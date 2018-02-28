from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import CredentialsField

from email_wrapper_lib.storage import Storage
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

    GOOGLE, MICROSOFT = range(2)
    PROVIDERS = (
        (GOOGLE, 'Google'),
        (MICROSOFT, 'Microsoft'),
    )

    id = models.BigAutoField(
        primary_key=True
    )
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
    raw_credentials = CredentialsField()
    status = models.PositiveSmallIntegerField(
        verbose_name=_('Status'),
        choices=ACCOUNT_STATUSES,
        default=NEW,
        db_index=True
    )
    provider_id = models.PositiveSmallIntegerField(
        verbose_name=_('Provider id'),
        choices=PROVIDERS,
        db_index=True
    )
    subscription_id = models.CharField(
        verbose_name=_('Subscription id'),
        null=True,
        max_length=255
    )

    # messages_total = models.BigIntegerField(
    #     verbose_name=_('Total number of messages')
    # )
    # threads_total = models.BigIntegerField(
    #     verbose_name=_('Total number of threads')
    # )

    @property
    def credentials(self):
        credentials = self.raw_credentials
        credentials.set_store(Storage(EmailAccount, 'id', self.pk, 'raw_credentials'))

        return credentials

    @property
    def manager(self):
        from email_wrapper_lib.providers import registry
        return registry[self.provider_id].manager(self)

    def __unicode__(self):
        return self.username

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailFolder(models.Model):
    SYSTEM, USER = range(2)
    FOLDER_TYPES = (
        (SYSTEM, _('System')),
        (USER, _('User')),
    )

    account = models.ForeignKey(
        to='email_wrapper_lib.EmailAccount',
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
        max_length=255,
        db_index=True
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

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('account', 'remote_id', 'remote_value')
        app_label = 'email_wrapper_lib'


class EmailMessage(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )
    remote_id = models.CharField(
        verbose_name=_('Remote id'),
        max_length=255
    )
    thread_id = models.CharField(
        verbose_name=_('Thread id'),
        max_length=255
    )
    mime_message_id = models.CharField(
        verbose_name=_('MIME message id'),
        max_length=255
    )
    account = models.ForeignKey(
        to='email_wrapper_lib.EmailAccount',
        on_delete=models.CASCADE,
        verbose_name=_('Account'),
        related_name='messages'
    )
    folders = models.ManyToManyField(
        to='email_wrapper_lib.EmailFolder',
        verbose_name=_('Folder'),
        related_name='messages'
    )
    recipients = models.ManyToManyField(
        to='email_wrapper_lib.EmailRecipient',
        through='email_wrapper_lib.EmailMessageToEmailRecipient',
        verbose_name=_('Recipients'),
        related_name='messages'
    )
    snippet = models.TextField(
        verbose_name=_('Snippet')
    )
    subject = models.TextField(
        verbose_name=_('Subject')
    )
    received_date_time = models.DateTimeField(
        verbose_name=_('Date')
    )
    is_read = models.BooleanField(
        verbose_name=_('Is read')
    )
    is_starred = models.BooleanField(
        verbose_name=_('Is starred')
    )
    has_attachments = models.BooleanField(
        verbose_name=_('Has attachment')
    )

    # TODO: set a property on the message to identify whether it's a reply, reply-all, forward, forward-multi or just a normal email.

    # Do we need the following? These are just labels and have no effect on how they are showed in the inbox and stuff?
    # is_draft = models.BooleanField(_('Is draft'))
    # is_important = models.BooleanField(_('Is important'))
    # is_archived = models.BooleanField(_('Is archived'))
    # is_trashed = models.BooleanField(_('Is trashed'))
    # is_spam = models.BooleanField(_('Is spam'))
    # is_sent = models.BooleanField(_('Is sent'))

    def get_recipients_by_type(self, recipient_type):
        if not hasattr(self, '_recipient_list'):
            # There is no cached version of the recipient list.
            self._message_to_recipient_list = EmailMessageToEmailRecipient.objects.filter(
                message_id=self.pk
            ).select_related('recipient')

        # Loop over Message Recipients and filter by recipient_type, return the recipient object.
        return [mr.recipient for mr in self._message_to_recipient_list if mr.recipient_type == recipient_type]

    @property
    def to_recipients(self):
        return self.get_recipients_by_type(EmailMessageToEmailRecipient.TO)

    @property
    def cc_recipients(self):
        return self.get_recipients_by_type(EmailMessageToEmailRecipient.CC)

    @property
    def bcc_recipients(self):
        return self.get_recipients_by_type(EmailMessageToEmailRecipient.BCC)

    @property
    def from_recipient(self):
        recipient_list = self.get_recipients_by_type(EmailMessageToEmailRecipient.FROM)
        # TODO: check if this is always one recipient, or if we actually need to return a list.
        return recipient_list[0] if recipient_list else None

    @property
    def sender_recipient(self):
        recipient_list = self.get_recipients_by_type(EmailMessageToEmailRecipient.SENDER)
        # TODO: check if this is always one recipient, or if we actually need to return a list.
        return recipient_list[0] if recipient_list else None

    @property
    def reply_to_recipient(self):
        recipient_list = self.get_recipients_by_type(EmailMessageToEmailRecipient.REPLY_TO)
        # TODO: check if this is always one recipient, or if we actually need to return a list.
        return recipient_list[0] if recipient_list else None

    def __unicode__(self):
        return u'{} - {} linked to account {}.'.format(self.id, self.remote_id, self.account_id)

    class Meta:
        app_label = 'email_wrapper_lib'


EmailMessageToEmailFolder = EmailMessage.folders.through


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
        max_length=509,  # 255 (name) + 254 (email_address)
        unique=True,
        db_index=True,
        editable=False
    )

    def __unicode__(self):
        return self.name

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
        to='email_wrapper_lib.EmailMessage',
        on_delete=models.CASCADE,
        verbose_name=_('Message')
    )
    recipient = models.ForeignKey(
        to='email_wrapper_lib.EmailRecipient',
        on_delete=models.CASCADE,
        verbose_name=_('Recipient')
    )
    recipient_type = models.PositiveSmallIntegerField(
        verbose_name=_('Recipient type'),
        choices=RECIPIENT_TYPES
    )

    class Meta:
        app_label = 'email_wrapper_lib'
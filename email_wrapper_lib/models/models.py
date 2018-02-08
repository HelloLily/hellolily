from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import CredentialsField

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
    credentials = CredentialsField()
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
    def manager(self):
        from email_wrapper_lib.providers import registry
        return registry[self.provider_id].manager(self)

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
    message_id = models.CharField(
        verbose_name=_('Message id'),
        max_length=255
    )
    account = models.ForeignKey(
        to='email_wrapper_lib.EmailAccount',
        on_delete=models.CASCADE,
        verbose_name=_('Account'),
        related_name='messages'
    )
    folder = models.ManyToManyField(
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
    snippet = models.CharField(
        verbose_name=_('Snippet'),
        max_length=255
    )
    subject = models.CharField(
        verbose_name=_('Subject'),
        max_length=255
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

    # Do we need the following? These are just labels and have no effect on how they are showed in the inbox and stuff?
    # is_draft = models.BooleanField(_('Is draft'))
    # is_important = models.BooleanField(_('Is important'))
    # is_archived = models.BooleanField(_('Is archived'))
    # is_trashed = models.BooleanField(_('Is trashed'))
    # is_spam = models.BooleanField(_('Is spam'))
    # is_sent = models.BooleanField(_('Is sent'))

    def get_recipients_by_type(self, recipient_type):
        # TODO: check if this caching works as intended.

        if hasattr(self, '_recipient_type_{}'.format(recipient_type)):
            return getattr(self, '_recipient_type_{}'.format(recipient_type))
        elif hasattr(self, '_prefetched_objects_cache') and 'recipients' in self._prefetched_objects_cache:
            return [rec for rec in self.recipients.all() if rec.recipient_type == recipient_type]
        else:
            recipients = self.recipients.filter(recipient_type=recipient_type)
            setattr(self, '_recipient_type_{}'.format(recipient_type), recipients)
            return recipients

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
        self.raw_value = '{0} <{1}>'.format(self.name, self.email_address)
        super(EmailRecipient, self).save(*args, **kwargs)

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

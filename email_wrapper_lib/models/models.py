from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2client.contrib.django_orm import CredentialsField, Storage

from email_wrapper_lib.providers import registry

from .mixins import TimeStampMixin, SoftDeleteMixin


class EmailAccount(SoftDeleteMixin, TimeStampMixin, models.Model):
    # id = models.BigAutoField(primary_key=True)
    username = models.CharField(_('username'), unique=True, max_length=255)
    user_id = models.CharField(_('user id'), unique=True, max_length=255)

    credentials = CredentialsField()

    # TODO: figure out which of these syncing indicators we actually need.
    is_active = models.BooleanField(default=True)
    is_syncing = models.BooleanField(default=False)
    is_broken = models.BooleanField(default=False)  # Perhaps: has_errors

    provider_id = models.SmallIntegerField(_('provider id'), choices=registry.choices, db_index=True)
    subscription_id = models.CharField(_('subscription id'), null=True, max_length=255)

    history_token = models.CharField(_('history token'), null=True, max_length=255)
    page_token = models.CharField(_('page token'), null=True, max_length=255)

    @classmethod
    def create_account_from_code(cls, provider, code):
        credentials = provider.flow.step2_exchange(code=code)
        connector = provider.connector(credentials, 'me')
        profile = connector.profile.get()

        account, created = EmailAccount.objects.get_or_create(
            username=profile['username'],
            user_id=profile['user_id'],
            provider_id=provider.id,
        )

        # Set the store so the credentials will auto refresh.
        credentials.set_store(Storage(cls, 'id', account.pk, 'credentials'))

        account.is_active = True
        account.credentials = credentials

        account.save(update_fields=['is_active', 'credentials'])

        return account

    class Meta:
        app_label = 'email_wrapper_lib'


class EmailRecipient(models.Model):
    name = models.CharField(_('name'), max_length=255)
    email_address = models.EmailField(_('email'))

    class Meta:
        unique_together = ('name', 'email_address')
        app_label = 'email_wrapper_lib'


class EmailFolder(models.Model):
    # For nesting, this is the parent label/folder.
    parent = models.OneToOneField('self', verbose_name=_('parent'), null=True)
    # The id from the provider.
    remote_id = models.CharField(_('remote id'), max_length=255)
    # The remote value, in gmail nesting is done with slashes like so: parent/child/subchild.
    remote_value = models.CharField(_('remote value'), max_length=255)
    # The actual name to display for the label/folder.
    name = models.CharField(_('name'), max_length=255)

    class Meta:
        unique_together = ('remote_id', 'remote_value')
        app_label = 'email_wrapper_lib'


class EmailMessage(models.Model):
    # id = models.BigAutoField(primary_key=True)
    remote_id = models.CharField(_('remote id'), max_length=255)
    thread_id = models.CharField(_('thread id'), max_length=255)
    message_id = models.CharField(_('message id'), max_length=255)

    account = models.ForeignKey(EmailAccount, verbose_name=_('account'), related_name='db_messages')
    folder = models.ManyToManyField(EmailFolder, verbose_name=_('folder'), related_name='messages')

    to = models.ManyToManyField(EmailRecipient, verbose_name=_('to'), related_name='messages_received')
    cc = models.ManyToManyField(EmailRecipient, verbose_name=_('cc'), related_name='messages_received_cc')
    bcc = models.ManyToManyField(EmailRecipient, verbose_name=_('bcc'), related_name='messages_received_bcc')
    sender = models.ForeignKey(EmailRecipient, verbose_name=_('sender'), related_name='messages_sent')
    reply_to = models.ForeignKey(EmailRecipient, verbose_name=_('reply_to'), related_name='messages_reply_to')

    snippet = models.CharField(_('snippet'), max_length=255)
    subject = models.CharField(_('subject'), max_length=255)
    date = models.DateTimeField(_('date'))

    is_read = models.BooleanField(_('is read'))
    is_starred = models.BooleanField(_('is starred'))
    is_draft = models.BooleanField(_('is draft'))
    is_important = models.BooleanField(_('is important'))
    is_archived = models.BooleanField(_('is archived'))
    is_trashed = models.BooleanField(_('is trashed'))
    is_spam = models.BooleanField(_('is spam'))
    is_sent = models.BooleanField(_('is sent'))

    class Meta:
        app_label = 'email_wrapper_lib'

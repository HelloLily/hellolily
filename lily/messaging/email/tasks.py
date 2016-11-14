import logging
import traceback

from celery.task import task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from oauth2client.client import HttpAccessTokenRefreshError

from lily.utils.functions import post_intercom_event
from .manager import GmailManager
from .models.models import (EmailAccount, EmailMessage, EmailOutboxMessage, EmailTemplateAttachment,
                            EmailOutboxAttachment, EmailAttachment)

logger = logging.getLogger(__name__)


@task(name='synchronize_email_account_scheduler')
def synchronize_email_account_scheduler():
    """
    Start new tasks for every active mailbox to start synchronizing.
    """
    for email_account in EmailAccount.objects.filter(is_authorized=True, is_deleted=False):
        logger.debug('Scheduling sync for %s', email_account.email_address)

        if not email_account.history_id:
            # First synchronize
            logger.debug('Adding task for first sync for %s', email_account.email_address)
            first_synchronize_email_account.apply_async(
                args=(email_account.pk,),
                max_retries=1,
                default_retry_delay=100,
            )
        else:
            # Incremental synchronize
            logger.info('Adding task for sync for: %s', email_account.email_address)
            synchronize_email_account.apply_async(
                args=(email_account.pk,),
                max_retries=1,
                default_retry_delay=100,
            )

        logger.info('Adding task for label sync for: %s', email_account.email_address)
        synchronize_labels.apply_async(
            args=(email_account.pk,),
            max_retries=1,
            default_retry_delay=100,
        )


@task(name='synchronize_email_account', logger=logger)
def synchronize_email_account(account_id):
    """
    Synchronize task for all email accounts that are connected with gmail api.

    Args:
        account_id (int): id of the EmailAccount
    """
    try:
        email_account = EmailAccount.objects.get(pk=account_id, is_deleted=False)
    except EmailAccount.DoesNotExist:
        logger.warning('EmailAccount no longer exists: %s', account_id)
        return False
    else:
        if email_account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_account)
                manager.sync_by_history()
                logger.info('History page sync done for: %s', email_account)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_account.email_address)
                pass
            except Exception:
                logger.exception('No sync for account %s' % email_account)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_account.email_address)


@task(name='first_synchronize_email_account', logger=logger)
def first_synchronize_email_account(account_id):
    """
    First Synchronize task for all email accounts that are connected with gmail api.

    Args:
        account_id (int): id of the EmailAccount
    """
    try:
        email_account = EmailAccount.objects.get(pk=account_id, is_deleted=False)
    except EmailAccount.DoesNotExist:
        logger.warning('EmailAccount no longer exists: %s', account_id)
    else:
        if email_account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_account)
                logger.debug('First sync for: %s', email_account)
                manager.full_synchronize()
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_account.email_address)
                pass
            except Exception:
                logger.exception('No sync for account %s' % email_account)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_account.email_address)


@task(name='first_sync_finished', logger=logger)
def first_sync_finished(account_id):
    """
    Mark the email account as finished syncing for the first time.

    Args:
        account_id (int): id of the EmailAccount
    """
    try:
        email_account = EmailAccount.objects.get(pk=account_id, is_deleted=False)
    except EmailAccount.DoesNotExist:
        logger.warning('EmailAccount no longer exists: %s', account_id)
    else:
        if email_account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_account)
                logger.debug('Finished first email sync for: %s', email_account)
                email_account.first_sync_finished = True
                email_account.save()
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_account.email_address)
                pass
            except Exception:
                logger.exception('Could not update first_sync_finished flag for account %s' % email_account)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_account.email_address)


@task(name='synchronize_labels', logger=logger)
def synchronize_labels(account_id):
    """
    Synchronize the labels for the email account.

    Args:
        account_id (int): id of the EmailAccount
    """
    try:
        email_account = EmailAccount.objects.get(pk=account_id, is_deleted=False)
    except EmailAccount.DoesNotExist:
        logger.warning('EmailAccount no longer exists: %s', account_id)
    else:
        if email_account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_account)
                manager.sync_labels()
                logger.debug('Label synchronize for: %s', email_account)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_account.email_address)
                pass
            except Exception:
                logger.exception('Could not synchronize labels for account %s' % email_account)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_account.email_address)


@task(name='download_email_message', logger=logger, acks_late=True, bind=True)
def download_email_message(self, account_id, message_id):
    """
    Download message.

    Args:
        account_id (int): id of the EmailAccount
        message_id (str): google id of EmailMessage
    """
    try:
        email_account = EmailAccount.objects.get(pk=account_id, is_deleted=False)
    except EmailAccount.DoesNotExist:
        logger.warning('EmailAccount no longer exists: %s', account_id)
    else:
        if email_account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_account)
                logger.debug('Fetch message %s for: %s' % (message_id, email_account))
                manager.download_message(message_id)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_account.email_address)
                pass
            except Exception as exc:
                logger.exception('Fetch message %s for: %s failed' % (message_id, email_account))
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_account.email_address)


@task(name='update_labels_for_message', logger=logger, bind=True)
def update_labels_for_message(self, account_id, email_id):
    """
    Add and/or removes labels for the EmailMessage.

    Args:
        account_id (id): EmailAccount id
        email_id (str): Google hash of their id
    """
    try:
        email_account = EmailAccount.objects.get(pk=account_id, is_deleted=False)
    except EmailAccount.DoesNotExist:
        logger.warning('EmailAccount no longer exists: %s', email_id)
    else:
        if email_account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_account)
                logger.debug('Changing labels for: %s', email_id)
                manager.update_labels_for_message(email_id)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_account.email_address)
                pass
            except Exception as exc:
                logger.exception('Failed changing labels for %s' % email_id)
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_account.email_address)


@task(name='toggle_read_email_message', logger=logger, acks_late=True, bind=True)
def toggle_read_email_message(self, email_id, read=True):
    """
    Mark message as read or unread.

    Args:
        email_id (int): id of the EmailMessage
        read (boolean, optional): if True, message will be marked as read
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
    except EmailMessage.DoesNotExist:
        logger.debug('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                logger.debug('Toggle read: %s', email_message)
                manager.toggle_read_email_message(email_message, read=read)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception as exc:
                logger.exception('Failed toggle read for: %s' % email_message)
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)


@task(name='archive_email_message', logger=logger, bind=True)
def archive_email_message(self, email_id):
    """
    Archive message.

    Args:
        email_id (int): id of the EmailMessage
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
    except EmailMessage.DoesNotExist:
        logger.warning('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                logger.debug('Archiving: %s', email_message)
                manager.archive_email_message(email_message)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception as exc:
                logger.exception('Failed archiving %s' % email_message)
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)


@task(name='trash_email_message', logger=logger, bind=True)
def trash_email_message(self, email_id):
    """
    Trash message.

    Args:
        email_id (int): id of the EmailMessage
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
    except EmailMessage.DoesNotExist:
        logger.warning('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                logger.debug('Trashing: %s', email_message)
                if email_message.is_draft:
                    manager.delete_draft_email_message(email_message)
                else:
                    manager.trash_email_message(email_message)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception as exc:
                logger.exception('Failed trashing %s' % email_message)
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)


@task(name='add_and_remove_labels_for_message', logger=logger, bind=True)
def add_and_remove_labels_for_message(self, email_id, add_labels=None, remove_labels=None):
    """
    Add and/or removes labels for the EmailMessage.

    Args:
        email_id (id): EmailMessage id
        add_labels (list, optional): list of label_ids to add
        remove_labels (list, optional): list of label_ids to remove
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
    except EmailMessage.DoesNotExist:
        logger.warning('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                logger.debug('Changing labels for: %s', email_message)
                manager.add_and_remove_labels_for_message(email_message, add_labels, remove_labels)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception as exc:
                logger.exception('Failed changing labels for %s' % email_message)
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)


@task(name='delete_email_message', logger=logger, bind=True)
def delete_email_message(self, email_id):
    """
    Delete message.

    Args:
        email_id (int): id of the EmailMessage
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
        in_trash = email_message.is_trashed
    except EmailMessage.DoesNotExist:
        logger.warning('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                if email_message.is_draft:
                    manager.delete_draft_email_message(email_message)
                elif in_trash:
                    manager.delete_email_message(email_message)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception as exc:
                logger.exception('Failed deleting %s' % email_message)
                raise self.retry(exc=exc)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)


@task(name='send_message', logger=logger)
def send_message(email_outbox_message_id, original_message_id=None):
    """
    Send EmailOutboxMessage.

    Args:
        email_outbox_message_id (int): id of the EmailOutboxMessage
        original_message_id (int, optional): ID of the original EmailMessage
    """
    send_logger = logging.getLogger('email_errors_temp_logger')
    send_logger.info('Start sending email_outbox_message: %d' % (email_outbox_message_id,))

    sent_success = False
    try:
        email_outbox_message = EmailOutboxMessage.objects.get(pk=email_outbox_message_id)
    except EmailOutboxMessage.DoesNotExist:
        raise

    email_account = email_outbox_message.send_from
    if not email_account.is_authorized:
        logger.error('EmailAccount not authorized: %s', email_account)
        return sent_success

    # If we reply or forward, we want to add the thread_id.
    original_message_thread_id = None
    if original_message_id:
        try:
            original_message = EmailMessage.objects.get(pk=original_message_id)
            if original_message.account.id is email_account.id:
                original_message_thread_id = original_message.thread_id
        except EmailMessage.DoesNotExist:
            raise

    # Add template attachments.
    if email_outbox_message.template_attachment_ids:
        template_attachment_id_list = email_outbox_message.template_attachment_ids.split(',')
        for template_attachment_id in template_attachment_id_list:
            try:
                template_attachment = EmailTemplateAttachment.objects.get(pk=template_attachment_id)
            except EmailTemplateAttachment.DoesNotExist:
                pass
            else:
                attachment = EmailOutboxAttachment()
                attachment.content_type = template_attachment.content_type
                attachment.size = template_attachment.size
                attachment.email_outbox_message = email_outbox_message
                attachment.attachment = template_attachment.attachment
                attachment.tenant_id = template_attachment.tenant_id
                attachment.save()

    # Add attachment from original message (if mail is being forwarded).
    if email_outbox_message.original_attachment_ids:
        original_attachment_id_list = email_outbox_message.original_attachment_ids.split(',')
        for attachment_id in original_attachment_id_list:
            try:
                original_attachment = EmailAttachment.objects.get(pk=attachment_id)
            except EmailAttachment.DoesNotExist:
                pass
            else:
                outbox_attachment = EmailOutboxAttachment()
                outbox_attachment.email_outbox_message = email_outbox_message
                outbox_attachment.tenant_id = original_attachment.message.tenant_id

                file = default_storage._open(original_attachment.attachment.name)
                file.open()
                content = file.read()
                file.close()

                file = ContentFile(content)
                file.name = original_attachment.attachment.name

                outbox_attachment.attachment = file
                outbox_attachment.inline = original_attachment.inline
                outbox_attachment.size = file.size
                outbox_attachment.save()

    manager = None
    try:
        manager = GmailManager(email_account)
        manager.send_email_message(email_outbox_message.message(), original_message_thread_id)
        logger.debug('Message sent from: %s', email_account)
        # Seems like everything went right, so the EmailOutboxMessage object isn't needed any more.
        email_outbox_message.delete()
        sent_success = True
        # TODO: This should probably be moved to the front end once.
        # We can notify users about sent mails.
        post_intercom_event(event_name='email-sent', user_id=email_account.owner.id)
    except HttpAccessTokenRefreshError:
        logger.warning('EmailAccount not authorized: %s', email_account.email_address)
        pass
    except Exception as e:
        logger.error(traceback.format_exc(e))
        raise
    finally:
        if manager:
            manager.cleanup()

    send_logger.info(
        'Done sending email_outbox_message: %d And sent_succes value: %s' % (email_outbox_message_id, sent_success)
    )
    return sent_success


@task(name='create_draft_email_message', logger=logger)
def create_draft_email_message(email_outbox_message_id):
    """
    Send EmailOutboxMessage.

    Args:
        email_outbox_message_id (int): id of the EmailOutboxMessage
    """
    draft_success = False
    try:
        email_outbox_message = EmailOutboxMessage.objects.get(pk=email_outbox_message_id)
    except EmailOutboxMessage.DoesNotExist:
        raise

    email_account = email_outbox_message.send_from

    if not email_account.is_authorized:
        logger.error('EmailAccount not authorized: %s', email_account)
        return draft_success

    manager = None
    try:
        manager = GmailManager(email_account)
        manager.create_draft_email_message(email_outbox_message.message())
        logger.debug('Message saved as draft for: %s', email_account)
        # Seems like everything went right, so the EmailOutboxMessage object isn't needed any more
        email_outbox_message.delete()
        draft_success = True
    except HttpAccessTokenRefreshError:
        logger.warning('EmailAccount not authorized: %s', email_account.email_address)
        pass
    except Exception:
        logger.exception('Couldn\'t create draft')
        raise
    finally:
        if manager:
            manager.cleanup()

    return draft_success


@task(name='update_draft_email_message', logger=logger)
def update_draft_email_message(email_outbox_message_id, current_draft_pk):
    """
    Send EmailOutboxMessage.

    Args:
        email_outbox_message_id (int): id of the EmailOutboxMessage
        current_draft_pk (int): id of the EmailMessage that is the current draft
    """
    draft_success = False
    email_outbox_message = EmailOutboxMessage.objects.get(pk=email_outbox_message_id)
    current_draft = EmailMessage.objects.get(pk=current_draft_pk)

    email_account = email_outbox_message.send_from

    if not email_account.is_authorized:
        logger.error('EmailAccount not authorized: %s', email_account)
        return draft_success

    manager = None
    try:
        manager = GmailManager(email_account)

        if current_draft.draft_id:
            # Update current draft.
            manager.update_draft_email_message(email_outbox_message.message(), draft_id=current_draft.draft_id)
            logger.debug('Updated draft for: %s', email_account)
        else:
            # There is no draft pk stored, just remove and create a new draft.
            manager.create_draft_email_message(email_outbox_message.message())
            manager.delete_email_message(current_draft)
            logger.debug('Message saved as draft and removed current draft, for: %s', email_account)

        # Seems like everything went right, so the EmailOutboxMessage object isn't needed any more.
        email_outbox_message.delete()
        draft_success = True
    except HttpAccessTokenRefreshError:
        logger.warning('EmailAccount not authorized: %s', email_account.email_address)
        pass
    except Exception:
        logger.exception('Couldn\'t create or update draft')
        raise
    finally:
        if manager:
            manager.cleanup()

    return draft_success


@task(name='toggle_star_email_message', logger=logger)
def toggle_star_email_message(email_id, star=True):
    """
    (Un)star a message.

    Args:
        email_id (int): id of the EmailMessage
        star (boolean, optional): if True, message will be starred
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
    except EmailMessage.DoesNotExist:
        logger.debug('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                logger.debug('Toggle star for: %s', email_message)
                manager.toggle_star_email_message(email_message, star)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception:
                logger.exception('Failed toggle star for: %s', email_message)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)


@task(name='toggle_spam_email_message', logger=logger)
def toggle_spam_email_message(email_id, spam=True):
    """
    (Un)mark message as spam.

    Args:
        email_id (int): id of the EmailMessage
        spam (boolean, optional): if True, message will be marked as spam
    """
    try:
        email_message = EmailMessage.objects.get(pk=email_id)
    except EmailMessage.DoesNotExist:
        logger.warning('EmailMessage no longer exists: %s', email_id)
    else:
        if email_message.account.is_authorized:
            manager = None
            try:
                manager = GmailManager(email_message.account)
                logger.debug('Toggle spam label for message: %s', email_message)
                manager.toggle_spam_email_message(email_message, spam)
            except HttpAccessTokenRefreshError:
                logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)
                pass
            except Exception:
                logger.exception('Failed marking as spam: %s', email_message)
            finally:
                if manager:
                    manager.cleanup()
        else:
            logger.warning('Not syncing, no authorization for: %s', email_message.account.email_address)

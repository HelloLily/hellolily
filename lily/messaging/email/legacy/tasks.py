from __future__ import absolute_import

import gc
import anyjson
import logging
import os
import traceback
from datetime import datetime, timedelta
from email import Encoders
from email.MIMEBase import MIMEBase

from Crypto import Random
from celery import task
from celery.signals import task_prerun
from dateutil.tz import tzutc
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db import connection, transaction
from imapclient import DRAFT

from lily.messaging.email.models import EmailAccount, EmailMessage, EmailHeader, OK_EMAILACCOUNT_AUTH, \
    NO_EMAILACCOUNT_AUTH, EmailAddressHeader, UNKNOWN_EMAILACCOUNT_AUTH, EmailOutboxMessage
from lily.messaging.email.task_utils import EmailMessageCreationError, save_email_message, save_headers, \
    save_attachments, get_headers_and_identifier, create_email_attachments, create_headers_query_string, \
    create_message_query_string
from lily.messaging.email.utils import LilyIMAP, smtp_connect, EmailMultiRelated, EmailMultiAlternatives, \
    get_attachment_filename_from_url
from lily.users.models import LilyUser
from python_imap.errors import IMAPConnectionError
from python_imap.folder import ALLMAIL, DRAFTS, TRASH, INBOX, SENT
from python_imap.utils import convert_html_to_text
from taskmonitor.decorators import monitor_task
from taskmonitor.utils import lock_task

# while profiling
# import sys
# from celery.utils.debug import sample_mem, memdump
# from django.template.defaultfilters import filesizeformat
# from lily.utils.background import meminspect
# from pympler.asizeof import asizeof


task_logger = logging.getLogger('celery_task')

LOCK_EXPIRE = 300  # lock expire in seconds

# cache.add failes if the key already exists
acquire_lock = lambda lock_id: cache.add(lock_id, "true", LOCK_EXPIRE)
release_lock = lambda lock_id: cache.delete(lock_id)   # pylint: disable=W0108


@task(name='synchronize_email_scheduler')
def synchronize_email_scheduler():
    """
    Start new tasks for every active mailbox to start synchronizing one or
    more folders.
    """
    lock_id = 'synchronize_email_scheduler'

    if acquire_lock(lock_id):  # this should always work, but just in case..
        try:
            task_logger.debug('synchronize scheduler starting')

            # Find email accounts which authentication info should be OK.
            email_accounts = EmailAccount.objects.filter(
                auth_ok__in=(OK_EMAILACCOUNT_AUTH, UNKNOWN_EMAILACCOUNT_AUTH),
                is_deleted=False,
            ).order_by('-last_sync_date')
            for email_account in email_accounts:
                email_address = email_account.email

                task_logger.debug('attempting sync for %s', email_address)
                if not email_account.last_sync_date:
                    locked, status = lock_task('retrieve_all_emails_for', email_account.id)
                    if not locked:
                        task_logger.debug('skipping task "retrieve_all_emails_for" for %s', email_address)
                        continue

                    task_logger.debug('syncing %s', email_address)

                    retrieve_all_emails_for.apply_async(
                        args=(email_account.id,),
                        max_retries=1,
                        default_retry_delay=100,
                        kwargs={'status_id': status.pk},
                    )
                else:
                    locked, status = lock_task('retrieve_new_emails_for', email_account.id)
                    if not locked:
                        task_logger.debug('skipping task "retrieve_new_emails_for" for %s', email_address)
                        continue

                    task_logger.debug('syncing %s', email_address)

                    retrieve_new_emails_for.apply_async(
                        args=(email_account.id,),
                        max_retries=1,
                        default_retry_delay=100,
                        kwargs={'status_id': status.pk},
                    )

            task_logger.debug('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.debug('synchronize scheduler already running')


@task(name='retrieve_new_emails_for', bind=True)
@monitor_task(logger=task_logger)
def retrieve_new_emails_for(emailaccount_id):
    """
    Download new emails via IMAP for an EmailAccount since
     *last_sync_date* unless there has been some period of inactivity.
    A period of inactivity is considered when:
        - the users that can access the email account have not logged in
          for 4 weeks (if the email account is owned by a user)
        - there is no user for that tenant who logged in for
          4 weeks (if the emai laccount is not owned by a user, but
          by a normal contact/account)
    """
    try:
        email_account = EmailAccount.objects.get(
            id=emailaccount_id,
            is_deleted=False,
        )
    except EmailAccount.DoesNotExist:
        pass
    else:
        # Check for inactivity
        now_utc = datetime.now(tzutc())
        last_login_utc = LilyUser.objects.filter(tenant=email_account.tenant).order_by('-last_login').values_list('last_login')[0][0]

        activity_timedelta = now_utc - last_login_utc
        if activity_timedelta > timedelta(days=28):
            # Period of inactivity for two weeks: skip synchronize for this email_account
            task_logger.debug('%s inactive for 28 days', email_account.email)
            return
        else:
            task_logger.debug('%s last activity was %s ago', email_account.email, str(activity_timedelta))

            # Download new messages since last synchronization if that was some time ago
            last_sync_date = email_account.last_sync_date
            if not last_sync_date:
                last_sync_date = datetime.fromtimestamp(0)
            last_sync_date_utc = last_sync_date.astimezone(tzutc())
            task_logger.debug('last synchronization for %s happened at %s', email_account.email, last_sync_date_utc)
            if now_utc - last_sync_date_utc > timedelta(minutes=5):
                task_logger.debug('start synchronizing folders for %s', email_account.email)
                datetime_since = last_sync_date.strftime('%d-%b-%Y %H:%M:%S')

                with LilyIMAP(email_account) as server:
                    if server.login(email_account.username, email_account.password):
                        email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                        email_account.save()

                        # Update folder list
                        before = datetime.now()
                        try:
                            email_account.folders = get_account_folders_from_server(server)
                            task_logger.debug(
                                'Retrieving IMAP folder list for %s in %ss',
                                email_account.email,
                                (datetime.now() - before).total_seconds()
                            )

                            folders = [server.get_folder(INBOX)]
                            allmail_folder = server.get_folder(ALLMAIL)
                        except IMAPConnectionError:
                            pass
                        else:
                            # Download full email messages from INBOX
                            modifiers_new = ['BODY[]', 'FLAGS', 'RFC822.SIZE']
                            criteria = ['UNSEEN SINCE "%s"' % datetime_since]
                            for folder in folders:
                                before = datetime.now()
                                synchronize_folder(
                                    email_account,
                                    server,
                                    folder,
                                    criteria=criteria,
                                    modifiers_new=modifiers_new,
                                    new_only=True,
                                    batch_size=10
                                )
                                task_logger.debug('Retrieving new messages in folder %s list since %s in %ss',
                                                 folder,
                                                 datetime_since,
                                                 (datetime.now() - before).total_seconds())

                            # Download headers from messages in ALLMAIL
                            modifiers_old = modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE']
                            criteria = ['SINCE "%s"' % datetime_since]

                            before = datetime.now()
                            synchronize_folder(
                                email_account,
                                server,
                                allmail_folder,
                                criteria=criteria,
                                modifiers_old=modifiers_old,
                                modifiers_new=modifiers_new,
                                new_only=True
                            )
                            task_logger.debug('Retrieving new messages in folder %s since %s list in %ss',
                                             allmail_folder,
                                             datetime_since,
                                             (datetime.now() - before).total_seconds())

                            # Update succesful sync date
                            email_account.last_sync_date = now_utc
                            email_account.save()
                    elif not server.auth_ok:
                        email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                        email_account.save()


@task(name='synchronize_low_priority_email_scheduler')
def synchronize_low_priority_email_scheduler():
    """
    Attempt to start a new task for every active mailbox to synchronize
    via IMAP.
    """
    lock_id = 'synchronize_low_priority_email_scheduler'

    if acquire_lock(lock_id):  # this should always work, but just in case..
        try:
            task_logger.debug('synchronize scheduler starting')

            # Find email accounts which authentication info should be OK.
            email_accounts = EmailAccount.objects.filter(
                auth_ok__in=(OK_EMAILACCOUNT_AUTH, UNKNOWN_EMAILACCOUNT_AUTH),
                is_deleted=False,
            ).order_by('-last_sync_date')
            for email_account in email_accounts:
                email_address = email_account.email

                task_logger.debug('attempting sync for %s', email_address)

                locked, status = lock_task('retrieve_low_priority_emails_for', email_account.id)
                if not locked:
                    task_logger.debug('skipping task "retrieve_low_priority_emails_for" for %s', email_address)
                    continue

                task_logger.debug('syncing %s', email_address)

                retrieve_low_priority_emails_for.apply_async(
                    args=(email_account.id,),
                    max_retries=1,
                    default_retry_delay=100,
                    kwargs={'status_id': status.pk},
                )

            task_logger.debug('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.debug('synchronize scheduler already running')


@task(name='retrieve_low_priority_emails_for', bind=True)
@monitor_task(logger=task_logger)
def retrieve_low_priority_emails_for(emailaccount_id):
    """
    Download emails via IMAP for an EmailAccount for other folders than INBOX
    unless there has been some period of inactivity.
    A period of inactivity is considered when:
        - the users that can access the email account have not logged in
          for 4 weeks (if the email account is owned by a user)
        - there is no user for that tenant who logged in for
          4 weeks (if the email account is not owned by a user, but
          by a normal contact/account)
    The downloaded emails are 47h59s old at max.
    """
    try:
        email_account = EmailAccount.objects.get(
            id=emailaccount_id,
            is_deleted=False,
        )
    except EmailAccount.DoesNotExist:
        pass
    else:
        # Check for inactivity
        now_utc = datetime.now(tzutc())
        last_login_utc = LilyUser.objects.filter(tenant=email_account.tenant).order_by('-last_login').values_list('last_login')[0][0]

        activity_timedelta = now_utc - last_login_utc
        if activity_timedelta > timedelta(days=28):
            # Period of inactivity for two weeks: skip synchronize for this email account
            task_logger.debug('%s inactive for 28 days', email_account.email)
            return
        else:
            task_logger.debug('%s last activity was %s ago', email_account.email, str(activity_timedelta))
            last_sync_date = email_account.last_sync_date
            if not last_sync_date:
                last_sync_date = datetime.fromtimestamp(0)
            last_sync_date_utc = last_sync_date.astimezone(tzutc())
            last_sync_date_utc -= timedelta(days=1)
            datetime_since = last_sync_date_utc.strftime('%d-%b-%Y 00:00:00')

            with LilyIMAP(email_account) as server:
                if server.login(email_account.username, email_account.password):
                    email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                    email_account.save()

                    # Update folder list
                    try:
                        email_account.folders = get_account_folders_from_server(server)
                        email_account.save()

                        folders = server.get_folders(exclude=[DRAFTS])
                        drafts_folder = server.get_folder(DRAFTS)
                    except IMAPConnectionError:
                        pass
                    else:
                        # Download email headers from messages in all folders except INBOX, DRAFTS, ALLMAIL
                        modifiers_new = ['BODY[]', 'FLAGS', 'RFC822.SIZE']
                        for folder in folders:
                            before = datetime.now()
                            synchronize_folder(
                                email_account,
                                server,
                                folder,
                                criteria=['SINCE "%s"' % datetime_since],
                                modifiers_new=modifiers_new,
                                new_only=True,
                                batch_size=10,
                            )
                            task_logger.debug('Retrieving new messages in folder %s list in %ss',
                                             folder,
                                             (datetime.now() - before).total_seconds())

                        # Download full messags from DRAFTS
                        modifiers_old = modifiers_new = ['BODY[]', 'FLAGS', 'RFC822.SIZE']
                        synchronize_folder(
                            email_account,
                            server,
                            drafts_folder,
                            modifiers_old=modifiers_old,
                            modifiers_new=modifiers_new,
                            batch_size=10,
                        )
                elif not server.auth_ok:
                    email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                    email_account.save()


@task(name='retrieve_all_emails_for', bind=True)
@monitor_task(logger=task_logger)
def retrieve_all_emails_for(emailaccount_id):
    """
    Download all emails via IMAP for an EmailAccount. This skips downloading
    the full body for e-mails.
    """
    try:
        email_account = EmailAccount.objects.get(
            id=emailaccount_id,
            is_deleted=False,
        )
    except EmailAccount.DoesNotExist:
        pass
    else:
        now_utc = datetime.now(tzutc())

        with LilyIMAP(email_account) as server:
            if server.login(email_account.username, email_account.password):
                email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                email_account.save()

                # Update folder list
                try:
                    email_account.folders = get_account_folders_from_server(server)
                    email_account.save()

                    folders = server.get_folders(exclude=[DRAFTS])
                    drafts_folder = server.get_folder(DRAFTS),
                except IMAPConnectionError:
                    pass
                else:
                    modifiers_new = ['BODY[]', 'FLAGS', 'RFC822.SIZE']
                    for folder in folders:
                        synchronize_folder(
                            email_account,
                            server,
                            folder,
                            criteria=['ALL'],
                            modifiers_new=modifiers_new,
                            new_only=True,
                            batch_size=10,
                        )

                    modifiers_old = modifiers_new = ['BODY[]', 'FLAGS', 'RFC822.SIZE']
                    synchronize_folder(
                        email_account,
                        server,
                        drafts_folder,
                        modifiers_old=modifiers_old,
                        modifiers_new=modifiers_new,
                        batch_size=10,
                    )

                    email_account.last_sync_date = now_utc
            elif not server.auth_ok:
                email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                email_account.save()


@task(name='synchronize_email_flags_scheduler')
def synchronize_email_flags_scheduler():
    """
    Attempt to start a new task for every active mailbox to synchronize
    via IMAP.
    """
    lock_id = 'synchronize_email_flags_scheduler'

    if acquire_lock(lock_id):  # this should always work, but just in case..
        try:
            task_logger.debug('synchronize scheduler starting')

            # Find email accounts which authentication info should be OK.
            email_accounts = EmailAccount.objects.filter(
                auth_ok__in=(OK_EMAILACCOUNT_AUTH, UNKNOWN_EMAILACCOUNT_AUTH),
                is_deleted=False,
            ).order_by('-last_sync_date')
            for email_account in email_accounts:
                email_address = email_account.email

                task_logger.debug('attempting sync for %s', email_address)
                locked, status = lock_task('retrieve_all_flags_for', email_account.id)
                if not locked:
                    task_logger.debug('skipping task "retrieve_all_flags_for" for %s', email_address)
                    continue

                task_logger.debug('syncing %s', email_address)

                retrieve_all_flags_for.apply_async(
                    args=(email_account.id,),
                    max_retries=1,
                    default_retry_delay=100,
                    kwargs={'status_id': status.pk},
                )

            task_logger.debug('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.debug('synchronize scheduler already running')


@task(name='retrieve_all_flags_for', bind=True)
@monitor_task(logger=task_logger)
def retrieve_all_flags_for(emailaccount_id):
    """
    Download all FLAGS for emails via IMAP for an EmailAccount. This skips downloading
    the full body for e-mails but only updates the status UNSEEN, DELETED etc.
    """
    try:
        email_account = EmailAccount.objects.get(
            id=emailaccount_id,
            is_deleted=False,
        )
    except EmailAccount.DoesNotExist:
        pass
    else:
        with LilyIMAP(email_account) as server:
            if server.login(email_account.username, email_account.password):
                email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                email_account.save()

                # Update folder list
                try:
                    email_account.folders = get_account_folders_from_server(server)
                    email_account.save()

                    modifiers_old = ['FLAGS']
                    folders = server.get_folders(exclude=[DRAFTS, TRASH, SENT])
                except IMAPConnectionError:
                    pass
                else:
                    for folder in folders:
                        synchronize_folder(
                            email_account,
                            server,
                            folder,
                            criteria=['ALL'],
                            modifiers_old=modifiers_old,
                            old_only=True,
                            batch_size=100,
                        )
            elif not server.auth_ok:
                email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                email_account.save()


@task(name='mark_messages')
def mark_messages(message_ids, read=True):
    """
    Mark n messages as (un)read in the background.
    """
    if not isinstance(message_ids, list):
        message_ids = [message_ids]

    # Determine folder_names per account
    folder_name_qs = EmailMessage.objects.filter(id__in=message_ids).values_list('account_id', 'folder_name', 'uid')
    len(folder_name_qs)

    # Create a more sensible dict with this information
    account_folders = {}
    for account_id, folder_name, message_uid in folder_name_qs:
        if not account_folders.get(account_id, False):
            account_folders[account_id] = {}
        folder_names = account_folders.get(account_id)
        if not account_folders[account_id].get(folder_name, False):
            account_folders[account_id][folder_name] = []
        folder_names[folder_name].append(message_uid)

    # Mark messages read in every appropriate account/folder
    for account_id, folders in account_folders.items():
        try:
            email_account = EmailAccount.objects.get(
                pk=account_id,
                is_deleted=False,
            )
        except EmailAccount.DoesNotExist:
            pass
        else:
            with LilyIMAP(email_account) as server:
                if server.login(email_account.username, email_account.password):
                    email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                    email_account.save()

                    try:
                        for folder_name, uids in folders.items():
                            folder = server.get_folder(folder_name)
                            uids = ','.join([str(val) for val in uids])
                            server.toggle_seen(folder, uids, seen=read)
                    except IMAPConnectionError:
                        EmailMessage.objects.filter(id__in=message_ids).update(is_seen=(not read))
                elif not server.auth_ok:
                    email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                    email_account.save()


@task(name='delete_messages')
def delete_messages(message_ids):
    """
    Delete n messages in the background.
    """
    if not isinstance(message_ids, list):
        message_ids = [message_ids]

    # Determine folder_names per account
    folder_name_qs = EmailMessage.objects.filter(id__in=message_ids).values_list('account_id', 'folder_name', 'uid')
    len(folder_name_qs)

    # Delete messages from database first for immediate effect
    EmailMessage.objects.filter(id__in=message_ids).delete()

    # Create a more sensible dict with this information
    account_folders = {}
    for account_id, folder_name, message_uid in folder_name_qs:
        if not account_folders.get(account_id, False):
            account_folders[account_id] = {}
        folder_names = account_folders.get(account_id)
        if not account_folders[account_id].get(folder_name, False):
            account_folders[account_id][folder_name] = []
        folder_names[folder_name].append(message_uid)

    # Delete in every appropriate account/folder
    for account_id, folders in account_folders.items():
        try:
            email_account = EmailAccount.objects.get(
                pk=account_id,
                is_deleted=False,
            )
        except EmailAccount.DoesNotExist:
            pass
        else:
            with LilyIMAP(email_account) as server:
                if server.login(email_account.username, email_account.password):
                    email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                    email_account.save()

                    try:
                        for folder_name, uids in folders.items():
                            folder = server.get_folder(folder_name)
                            uids = ','.join([str(val) for val in uids])
                            server.delete_messages(folder, uids)
                    except IMAPConnectionError:
                        # Delete failed, do not mark the message as deleted anymore.
                        EmailMessage.objects.filter(id__in=message_ids).update(is_deleted=False)
                        # TODO: warn user that delete has failed
                elif not server.auth_ok:
                    email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                    email_account.save()


@task(name='move_messages', bind=True)
@monitor_task(logger=task_logger)
def move_messages(message_ids, to_folder_name):
    """
    Move messages asynchronously.
    """
    if not isinstance(message_ids, list):
        message_ids = [message_ids]

    # Determine folder_names per account
    folder_name_qs = EmailMessage.objects.filter(id__in=message_ids).values_list('account_id', 'folder_name', 'uid')
    len(folder_name_qs)

    # Create a more sensible dict with this information
    account_folders = {}
    for account_id, folder_name, message_uid in folder_name_qs:
        if not account_folders.get(account_id, False):
            account_folders[account_id] = {}
        folder_names = account_folders.get(account_id)
        if not account_folders[account_id].get(folder_name, False):
            account_folders[account_id][folder_name] = []
        folder_names[folder_name].append(message_uid)

    # Delete in every appropriate account/folder
    for account_id, folders in account_folders.items():
        try:
            email_account = EmailAccount.objects.get(
                pk=account_id,
                is_deleted=False,
            )
        except EmailAccount.DoesNotExist:
            return False
        else:
            with LilyIMAP(email_account) as server:
                if server.login(email_account.username, email_account.password):
                    email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                    email_account.save()

                    # Move messages from origin folders to *target_folder*
                    try:
                        for folder_name, uids in folders.items():
                            from_folder = server.get_folder(folder_name)
                            created_target_folder = server.move_messages(uids, from_folder, to_folder_name)

                            # Update known folders
                            if created_target_folder:
                                email_account.folders = get_account_folders_from_server(server)

                        target_folder = server.get_folder(to_folder_name)
                    except IMAPConnectionError:
                        # Move failed, do not mark the message as deleted anymore.
                        EmailMessage.objects.filter(id__in=message_ids).update(is_deleted=False)
                        return False
                    else:
                        # Delete local messages
                        EmailMessage.objects.filter(id__in=message_ids).delete()

                        # Synchronize with target_folder
                        synchronize_folder(email_account, server, target_folder, new_only=True)
                elif not server.auth_ok:
                    email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                    email_account.save()

    return True

###
# HELPER METHODS
###


def get_account_folders_from_server(server):
    """
    Map folders existing on *server* in a format that is used in template rendering.
    """
    account_folders = {}

    try:
        all_folders = server.get_folders(cant_select=True)
    except IMAPConnectionError:
        pass
    else:
        for i in range(len(all_folders)):
            folder = all_folders[i]

            # Skip sub folders (they will be retrieved later on
            if folder.get_name(full=True).find('/') != -1:
                continue

            is_parent = '\\HasNoChildren' not in folder.flags
            folder_properties = {
                'flags': folder.flags,
                'is_parent': is_parent,
                'full_name': folder.get_name(full=True),
                'children': {},
            }
            account_folders[folder.get_name()] = folder_properties

            if is_parent:
                children = {}
                i += 1
                while i < len(all_folders) and '\\HasNoChildren' not in folder.flags:
                    child_folder = all_folders[i]
                    if child_folder.parent is not None and child_folder.parent == folder:
                        children[child_folder.get_name()] = {
                            'flags': child_folder.flags,
                            'parent': folder.get_name(full=True),
                            'full_name': child_folder.get_name(full=True),
                        }
                    else:
                        break
                    i += 1
                account_folders[folder.get_name()]['children'] = children

    return account_folders


@task(name='synchronize_folder')
def synchronize_folder(account, server, folder, criteria=None, modifiers_old=None, modifiers_new=None, old_only=False, new_only=False, batch_size=1000):  # pylint: disable=R0913
    """
    Fetch and store modifiers_old for UIDs already in the database and
    modifiers_new for UIDs that only exist remotely.
    """
    criteria = criteria or ['ALL']
    modifiers_old = modifiers_old or ['FLAGS']
    modifiers_new = modifiers_new or ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE']

    # Process messages in batches to save memory
    task_logger.debug('sync start for %s', unicode(folder.get_name()))

    # Find already known uids
    known_uids_qs = EmailMessage.objects.filter(account=account, folder_name=folder.name_on_server)
    if 'SEEN' in criteria:
        known_uids_qs = known_uids_qs.filter(is_seen=True)

    if 'UNSEEN' in criteria:
        known_uids_qs = known_uids_qs.filter(is_seen=False)

    known_uids = set(known_uids_qs.values_list('uid', flat=True))

    try:
        folder_count, remote_uids = server.get_uids(folder, criteria)  # pylint: disable=W0612

        # Get the difference between local and server uids
        new_uids = list(set(remote_uids).difference(known_uids))

        if not new_only:
            # UIDs that no longer exist in this folder
            removed_uids = list(known_uids.difference(set(remote_uids)))

            # Delete removed_uids from known_uids
            [known_uids.discard(x) for x in removed_uids]  # pylint: disable=W0106
            known_uids = list(known_uids)

            # Delete from database
            EmailMessage.objects.filter(account=account, folder_name=folder.name_on_server, uid__in=removed_uids).delete()

            if len(known_uids):
                # Renew modifiers_old for known_uids, TODO; check scenario where local_uids[x] has been moved/trashed
                for i in range(0, len(known_uids), batch_size):
                    folder_messages = server.get_messages(known_uids[i:i + batch_size], modifiers_old, folder)
                    if len(folder_messages) > 0:
                        save_email_messages(folder_messages, account, folder, new_messages=False)
                    del folder_messages

        if not old_only:
            if len(new_uids):
                # Retrieve modifiers_new for new_uids
                for i in range(0, len(new_uids), batch_size):
                    folder_messages = server.get_messages(new_uids[i:i + batch_size], modifiers_new, folder)
                    if len(folder_messages) > 0:
                        save_email_messages(folder_messages, account, folder, new_messages=True)
                    del folder_messages
    except IMAPConnectionError:
        pass

    task_logger.debug('sync done for %s', unicode(folder.get_name()))


@transaction.atomic
def save_email_messages(messages, account, folder, new_messages=False):
    """
    Save messages in database for account. Folder_name needs to be the server name.

    Arguments:
        messages (list): List of Message objects
        account (instance): EmailMessage object where message belong to
        folder (instance): Folder object where messages are stored
        new_messages (boolean): True if the messages are new
    """
    task_logger.debug('Saving %s messages for %s in %s in the database', len(messages), account.email, folder.name_on_server)
    try:
        update_email_attachments = {}
        update_inline_email_attachments = {}
        email_message_polymorphic_ctype = ContentType.objects.get_for_model(EmailMessage)

        if new_messages:
            task_logger.warning('Saving these messages with the ORM since they are new')

            new_email_headers = {}
            new_email_address_headers = {}
            new_email_attachments = {}
            new_inline_email_attachments = {}
            for message in messages:
                try:
                    email_headers, email_address_headers, email_attachments, inline_email_attachments = save_email_message(
                        message,
                        account,
                        folder,
                        email_message_polymorphic_ctype
                    )
                except EmailMessageCreationError:
                    pass
                else:
                    if email_headers:
                        new_email_headers.update({message.uid: email_headers})
                    if email_address_headers:
                        new_email_address_headers.update({message.uid: email_address_headers})
                    if email_attachments:
                        new_email_attachments.update({message.uid: email_attachments})
                    if inline_email_attachments:
                        new_inline_email_attachments.update({message.uid: inline_email_attachments})

            # Fetch message ids and uids
            email_messages = EmailMessage.objects.filter(
                account=account,
                uid__in=[message.uid for message in messages],
                folder_name=folder.name_on_server
            ).values_list('id', 'uid')

            # Link message ids to headers and (inline) attachments
            for message_id, message_uid in email_messages:
                header_obj_list = new_email_headers.get(message_uid)
                if header_obj_list:
                    for header_obj in header_obj_list:
                        header_obj.message_id = message_id

                email_address_header_obj_list = new_email_address_headers.get(message_uid)
                if email_address_header_obj_list:
                    for header_obj in email_address_header_obj_list:
                        header_obj.message_id = message_id

                attachment_obj_list = new_email_attachments.get(message_uid)
                if attachment_obj_list:
                    for attachment_obj in attachment_obj_list:
                        attachment_obj.message_id = message_id

                inline_attachment_obj_list = new_inline_email_attachments.get(message_uid)
                if inline_attachment_obj_list:
                    for attachment_obj in inline_attachment_obj_list:
                        attachment_obj.message_id = message_id

            # Save new_email_headers
            if new_email_headers:
                save_headers(new_email_headers, EmailHeader)

            # Save new_email_address_headers
            if new_email_address_headers:
                save_headers(new_email_address_headers, EmailAddressHeader)

            # Save attachments
            if new_email_attachments:
                save_attachments(new_email_attachments, tenant_id=account.tenant_id, folder=folder)

            # Save inline attachments
            if new_inline_email_attachments:
                save_attachments(new_inline_email_attachments, tenant_id=account.tenant_id, folder=folder, inline=True)

        elif not new_messages:
            task_logger.debug('Saving these messages with custom concatenated SQL since they need to be updated')

            # Build query string and parameter list
            total_query_string = ''
            total_param_list = []
            total_query_count = 0
            update_email_headers = {}
            update_email_address_headers = {}

            cursor = None
            if messages:
                cursor = connection.cursor()

            task_logger.debug('Looping through %s messages', len(messages))
            for message in messages:
                query_string, param_list, query_count = create_message_query_string(
                    message,
                    account_id=account.id,
                    folder_name=folder.name_on_server
                )
                total_query_string += query_string
                total_param_list.extend(param_list)
                total_query_count += query_count

                # Check for headers
                headers = message.get_headers()
                if headers:
                    email_headers, email_address_headers, message_identifier = get_headers_and_identifier(
                        headers,
                        message.get_sent_date(),
                        account.tenant_id
                    )
                    if email_headers:
                        update_email_headers.update({message.uid: email_headers})
                    if email_address_headers:
                        update_email_address_headers.update({message.uid: email_address_headers})

                # Check for attachments
                email_attachments = create_email_attachments(message.get_attachments(), tenant_id=account.tenant_id)
                if email_attachments:
                    update_email_attachments.update({message.uid: email_attachments})

                # Check for inline attachments
                inline_email_attachments = create_email_attachments(
                    message.get_inline_attachments().items(),
                    tenant_id=account.tenant_id,
                    inline=True
                )
                if inline_email_attachments:
                    update_inline_email_attachments.update({message.uid: inline_email_attachments})

            # Execute queries
            if total_query_count:
                task_logger.debug('Executing (%s) queries for e-mail messages', total_query_count)
                cursor.execute(total_query_string, total_param_list)

            # Fetch message ids
            email_message_uids = EmailMessage.objects.filter(
                account=account,
                uid__in=[message.uid for message in messages],
                folder_name=folder.name_on_server
            ).values_list('id', 'uid')

            # Link message ids to headers and (inline) attachments
            for message_id, message_uid in email_message_uids:
                header_obj_list = update_email_headers.get(message_uid)
                if header_obj_list:
                    for header_obj in header_obj_list:
                        header_obj.message_id = message_id

                email_address_header_obj_list = update_email_address_headers.get(message_uid)
                if email_address_header_obj_list:
                    for header_obj in email_address_header_obj_list:
                        header_obj.message_id = message_id

                attachment_obj_list = update_email_attachments.get(message_uid)
                if attachment_obj_list:
                    for attachment_obj in attachment_obj_list:
                        attachment_obj.message_id = message_id

                inline_attachment_obj_list = update_inline_email_attachments.get(message_uid)
                if inline_attachment_obj_list:
                    for attachment_obj in inline_attachment_obj_list:
                        attachment_obj.message_id = message_id

            # Build query string and parameter list
            total_query_string = ''
            total_param_list = []
            total_query_count = 0

            # Find existing headers per email message
            existing_headers_per_message = {}
            existing_headers_qs = EmailHeader.objects.filter(
                message_id__in=[message_id for message_id, message_uid in email_message_uids]
            ).values_list('message_id', 'name')
            for message_id, header_name in existing_headers_qs:
                headers = existing_headers_per_message.get(message_id, [])
                headers.append(header_name)
                existing_headers_per_message.update({message_id: headers})

            # Save update_email_headers
            if update_email_headers:
                query_string, param_list, query_count = create_headers_query_string(
                    update_email_headers,
                    existing_headers_per_message,
                    'email_emailheader'
                )
                total_query_string += query_string
                total_param_list.extend(param_list)
                total_query_count += query_count

            # Find existing email address headers per email message
            existing_email_address_headers_per_message = {}
            existing_email_address_headers_qs = EmailAddressHeader.objects.filter(
                message_id__in=[message_id for message_id, message_uid in email_message_uids]
            ).values_list('message_id', 'name')
            for message_id, header_name in existing_email_address_headers_qs:
                headers = existing_email_address_headers_per_message.get(message_id, [])
                headers.append(header_name)
                existing_email_address_headers_per_message.update({message_id: headers})

            # Save update_email_address_headers
            if update_email_address_headers:
                query_string, param_list, query_count = create_headers_query_string(
                    update_email_address_headers,
                    existing_email_address_headers_per_message,
                    'email_emailaddressheader'
                )
                total_query_string += query_string
                total_param_list.extend(param_list)
                total_query_count += query_count

            # Execute queries
            if total_query_count:
                task_logger.debug('Executing (%s) queries for headers', total_query_count)
                cursor = connection.cursor()
                cursor.execute(total_query_string, total_param_list)
            else:
                task_logger.debug('No queries to execute')

            if cursor:
                cursor.close()

        # Save attachments
        save_attachments(update_email_attachments, tenant_id=account.tenant_id, folder=folder)

        # Save inline attachments
        save_attachments(update_inline_email_attachments, tenant_id=account.tenant_id, folder=folder, inline=True)

    except Exception, e:  # pylint: disable=W0703
        print traceback.format_exc(e)
    finally:
        # Let garbage collection do it's job
        messages = None
        total_query_string = None
        total_param_list = None
        total_query_count = None
        update_email_headers = None
        update_email_address_headers = None
        email_messages = None
        existing_headers_qs = None

        gc.collect()

    task_logger.debug('Messages saved')


def _task_prerun_listener(**kwargs):
    """
    Because of a threading issue in the Crypto library (which seems to be intentional),
    we need to call the atfork function to sync the worker with it's PID.

    When this is not done we get exceptions during decryption of email username/password.
    """
    Random.atfork()
task_prerun.connect(_task_prerun_listener)


@task(name='get_from_imap', bind=True)
@monitor_task(logger=task_logger)
def get_from_imap(email_account_id, message_uid, folder_name, message_identifier, message_id, readonly):
    try:
        email_account = EmailAccount.objects.get(pk=email_account_id)

        with LilyIMAP(email_account) as server:
            if server.login(email_account.username, email_account.password):
                email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                email_account.save()

                task_logger.debug('Searching IMAP for %s in %s', message_uid, folder_name)

                try:
                    message = server.get_message(
                        message_uid,
                        ['BODY[]', 'FLAGS', 'RFC822.SIZE'],
                        server.get_folder(folder_name),
                        readonly=readonly
                    )
                except IMAPConnectionError:
                    pass
                else:
                    if message:
                        task_logger.debug('Message retrieved, saving in database')
                        save_email_messages([message], email_account, message.folder)

                        duplicate_emails = EmailMessage.objects.filter(message_identifier=message_identifier)
                        for duplicate_email in duplicate_emails:
                            duplicate_email.body_text = message.get_text_body()
                            duplicate_email.body_html = message.get_html_body()
                            duplicate_email.save()
            elif not server.auth_ok:
                email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                email_account.save()
    except Exception, e:
        task_logger.error(traceback.format_exc(e))
        return None
    finally:
        # Let garbage collection do it's job
        email_account = None
        server = None
        message = None
        duplicate_emails = None
        email_account_id = None
        message_uid = None
        folder_name = None
        message_identifier = None
        readonly = None

        gc.collect()

    return {'message_id': message_id}


@task(name='send_message', bind=True)
@monitor_task(logger=task_logger)
def send_message(email_account_id, email_outbox_message_id):
    try:
        email_outbox_message = EmailOutboxMessage.objects.get(pk=email_outbox_message_id)
    except EmailOutboxMessage.DoesNotExist:
        return False

    to = anyjson.loads(email_outbox_message.to)
    cc = anyjson.loads(email_outbox_message.cc)
    bcc = anyjson.loads(email_outbox_message.bcc)

    send_from = email_outbox_message.send_from

    if send_from.from_name:
        # Add account name to From header if one is available
        from_email = '%s (%s)' % (send_from.from_name, send_from.email)
    else:
        # Otherwise only add the email address
        from_email = send_from.email

    message_data = dict(
        subject=email_outbox_message.subject,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
        headers=anyjson.loads(email_outbox_message.headers),
        body=convert_html_to_text(email_outbox_message.body, keep_linebreaks=True),
        connection=None,
        attachments=None,
        alternatives=None,
    )

    if email_outbox_message.mapped_attachments != 0:
        # Attach an HTML version as alternative to *body*
        email_message = EmailMultiAlternatives(**message_data)
    else:
        # Use multipart/related when sending inline images
        email_message = EmailMultiRelated(**message_data)

    email_message.attach_alternative(email_outbox_message.body, 'text/html')

    attachments = email_outbox_message.attachments.all()

    for attachment in attachments:
        try:
            storage_file = default_storage._open(attachment.attachment.name)
        except IOError, e:
            task_logger.error(traceback.format_exc(e))
            return False

        filename = get_attachment_filename_from_url(attachment.attachment.name)

        storage_file.open()
        content = storage_file.read()
        storage_file.close()

        filetype = attachment.content_type.split('/')
        part = MIMEBase(filetype[0], filetype[1])
        part.set_payload(content)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))

        email_message.attach(part)

    try:
        email_account = EmailAccount.objects.get(pk=email_account_id)
    except EmailAccount.DoesNotExist, e:
        task_logger.error(traceback.format_exc(e))
        return False

    try:
        with LilyIMAP(email_account) as server:
            if server.login(email_account.username, email_account.password):
                email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                email_account.save()

            # Send initial message
            connection = smtp_connect(email_account, fail_silently=False)
            connection.send_messages([email_message])

            # Send extra for BCC recipients if any
            if email_message.bcc:
                recipients = email_message.bcc

                # Send separate messages
                for recipient in recipients:
                    email_message.bcc = []
                    email_message.to = [recipient]
                    connection.send_messages([email_message])
            connection.close()

            # Synchronize only new messages from folder *SENT*
            synchronize_folder(
                email_account,
                server,
                server.get_folder(SENT),
                criteria=['subject "%s"' % email_message.subject],
                new_only=True
            )
    except Exception, e:
        task_logger.error(traceback.format_exc(e))
        return False
    finally:
        # Let garbage collection do it's job
        to = None
        cc = None
        bcc = None
        server = None
        email_account = None
        email_message = None
        connection = None
        email_account_id = None
        email_outbox_message_id = None

        gc.collect()

    # Seems like everything went right, so the EmailOutboxMessage object isn't needed any more
    email_outbox_message.delete()
    return True


@task(name='save_message', bind=True)
@monitor_task(logger=task_logger)
def save_message(email_account_id, email_outbox_message_id):
    try:
        email_outbox_message = EmailOutboxMessage.objects.get(pk=email_outbox_message_id)
    except EmailOutboxMessage.DoesNotExist:
        return False

    to = anyjson.loads(email_outbox_message.to)
    cc = anyjson.loads(email_outbox_message.cc)
    bcc = anyjson.loads(email_outbox_message.bcc)

    send_from = email_outbox_message.send_from

    if send_from.from_name:
        # Add account name to From header if one is available
        from_email = '%s (%s)' % (send_from.from_name, send_from.email)
    else:
        # Otherwise only add the email address
        from_email = send_from.email

    message_data = dict(
        subject=email_outbox_message.subject,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
        headers=anyjson.loads(email_outbox_message.headers),
        body=convert_html_to_text(email_outbox_message.body, keep_linebreaks=True),
        connection=None,
        attachments=None,
        alternatives=None,
    )

    if email_outbox_message.mapped_attachments != 0:
        # Attach an HTML version as alternative to *body*
        email_message = EmailMultiAlternatives(**message_data)
    else:
        # Use multipart/related when sending inline images
        email_message = EmailMultiRelated(**message_data)

    email_message.attach_alternative(email_outbox_message.body, 'text/html')

    attachments = email_outbox_message.attachments.all()

    for attachment in attachments:
        try:
            storage_file = default_storage._open(attachment.attachment.name)
        except IOError, e:
            task_logger.error(traceback.format_exc(e))
            return False

        filename = get_attachment_filename_from_url(attachment.attachment.name)

        storage_file.open()
        content = storage_file.read()
        storage_file.close()

        filetype = attachment.content_type.split('/')
        part = MIMEBase(filetype[0], filetype[1])
        part.set_payload(content)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))

        email_message.attach(part)
    try:
        email_account = EmailAccount.objects.get(pk=email_account_id)
    except EmailAccount.DoesNotExist, e:
        task_logger.error(traceback.format_exc(e))
        return False

    try:
        with LilyIMAP(email_account) as server:
            if server.login(email_account.username, email_account.password):
                email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                email_account.save()

            # Save *email_message* as draft
            folder = server.get_folder(DRAFTS)

            message_string = email_message.message().as_string(unixfrom=False)

            # Save draft remotely
            uid = server.append(
                folder,
                message_string,
                flags=[DRAFT]
            )

            # Sync this specific message
            message = server.get_message(
                uid,
                modifiers=['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE'],
                folder=folder
            )

            save_email_messages(
                [message],
                email_account,
                folder,
                new_messages=True
            )

            new_draft = EmailMessage.objects.get(
                account=email_account,
                uid=uid,
                folder_name=folder.name_on_server
            )

            # Seems like everything went right, so the EmailOutboxMessage object isn't needed any more
            email_outbox_message.delete()

            return new_draft.pk
    except IMAPConnectionError:
        return None
    finally:
        # Let garbage collection do it's job
        email_outbox_message = None
        attachments = None
        to = None
        cc = None
        bcc = None
        message = None
        folder = None
        email_account = None
        content = None
        uid = None
        new_draft = None

        gc.collect()


@task(name='remove_draft', bind=True)
@monitor_task(logger=task_logger)
def remove_draft(email_account_id, email_uid):
    try:
        email_account = EmailAccount.objects.get(pk=email_account_id)
    except EmailAccount.DoesNotExist, e:
        task_logger.error(traceback.format_exc(e))
        return False

    try:
        with LilyIMAP(email_account) as server:
            if server.login(email_account.username, email_account.password):
                email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                email_account.save()

                folder = server.get_folder(DRAFTS)
                server.delete_messages(folder, [email_uid])

    except IMAPConnectionError:
        return None
    finally:
        # Let garbage collection do it's job
        email_account = None
        folder = None
        server = None

        gc.collect()


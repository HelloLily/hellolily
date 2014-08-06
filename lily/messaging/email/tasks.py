from __future__ import absolute_import

import gc
import logging
import StringIO
import traceback
from datetime import datetime, timedelta
from email.utils import getaddresses

from Crypto import Random
from celery import task
from celery.signals import task_prerun
from dateutil.tz import tzutc
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.utils.html import escape
from imapclient import SEEN, DELETED

from lily.messaging.email.models import EmailAccount, EmailMessage, EmailHeader, EmailAttachment, OK_EMAILACCOUNT_AUTH, NO_EMAILACCOUNT_AUTH, \
    EmailAddressHeader
from lily.messaging.email.utils import get_attachment_upload_path, replace_anchors_in_html, replace_cid_in_html, LilyIMAP
from lily.users.models import CustomUser
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
            task_logger.info('synchronize scheduler starting')

            # Find email accounts which authentication info should be OK.
            email_accounts = EmailAccount.objects.filter(auth_ok__gt=NO_EMAILACCOUNT_AUTH).order_by('-last_sync_date')
            for email_account in email_accounts:
                email_address = email_account.email.email_address

                task_logger.info('attempting sync for %s', email_address)
                if not email_account.last_sync_date:
                    locked, status = lock_task('retrieve_all_emails_for', email_account.id)
                    if not locked:
                        task_logger.info('skipping task "retrieve_all_emails_for" for %s', email_address)
                        continue

                    task_logger.info('syncing %s', email_address)

                    retrieve_all_emails_for.apply_async(
                        args=(email_account.id,),
                        max_retries=1,
                        default_retry_delay=100,
                        kwargs={'status_id': status.pk},
                    )
                else:
                    locked, status = lock_task('retrieve_new_emails_for', email_account.id)
                    if not locked:
                        task_logger.info('skipping task "retrieve_new_emails_for" for %s', email_address)
                        continue

                    task_logger.info('syncing %s', email_address)

                    retrieve_new_emails_for.apply_async(
                        args=(email_account.id,),
                        max_retries=1,
                        default_retry_delay=100,
                        kwargs={'status_id': status.pk},
                    )

            task_logger.info('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.info('synchronize scheduler already running')


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
        email_account = EmailAccount.objects.get(id=emailaccount_id)
    except EmailAccount.DoesNotExist:
        pass
    else:
        # Check for inactivity
        now_utc = datetime.now(tzutc())
        last_login_utc = CustomUser.objects.filter(tenant=email_account.tenant).order_by('-last_login').values_list('last_login')[0][0]

        activity_timedelta = now_utc - last_login_utc
        if activity_timedelta > timedelta(days=28):
            # Period of inactivity for two weeks: skip synchronize for this email_account
            task_logger.info('%s inactive for 28 days', email_account.email.email_address)
            return
        else:
            task_logger.info('%s last activity was %s ago', email_account.email.email_address, str(activity_timedelta))

            # Download new messages since last synchronization if that was some time ago
            last_sync_date = email_account.last_sync_date
            if not last_sync_date:
                last_sync_date = datetime.fromtimestamp(0)
            last_sync_date_utc = last_sync_date.astimezone(tzutc())
            task_logger.info('last synchronization for %s happened at %s', email_account.email.email_address, last_sync_date_utc)
            if now_utc - last_sync_date_utc > timedelta(minutes=5):
                task_logger.info('start synchronizing folders for %s', email_account.email.email_address)
                datetime_since = last_sync_date.strftime('%d-%b-%Y %H:%M:%S')

                with LilyIMAP(email_account) as server:
                    if server.login(email_account.username, email_account.password):
                        email_account.auth_ok = OK_EMAILACCOUNT_AUTH
                        email_account.save()

                        # Update folder list
                        before = datetime.now()
                        try:
                            email_account.folders = get_account_folders_from_server(server)
                            task_logger.info('Retrieving IMAP folder list for %s in %ss',
                                             email_account.email.email_address,
                                             (datetime.now() - before).total_seconds())

                            folders = [server.get_folder(INBOX)]
                            allmail_folder = server.get_folder(ALLMAIL)
                        except IMAPConnectionError:
                            pass
                        else:
                            # Download full email messages from INBOX
                            modifiers_new = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE']
                            criteria = ['UNSEEN SINCE "%s"' % datetime_since]
                            for folder in folders:
                                before = datetime.now()
                                synchronize_folder(
                                    email_account,
                                    server,
                                    folder,
                                    criteria=criteria,
                                    modifiers_new=modifiers_new,
                                    new_only=True
                                )
                                task_logger.info('Retrieving new messages in folder %s list since %s in %ss',
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
                            task_logger.info('Retrieving new messages in folder %s since %s list in %ss',
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
            task_logger.info('synchronize scheduler starting')

            # Find email accounts which authentication info should be OK.
            email_accounts = EmailAccount.objects.filter(auth_ok__gt=NO_EMAILACCOUNT_AUTH).order_by('-last_sync_date')
            for email_account in email_accounts:
                email_address = email_account.email.email_address

                task_logger.info('attempting sync for %s', email_address)

                locked, status = lock_task('retrieve_low_priority_emails_for', email_account.id)
                if not locked:
                    task_logger.info('skipping task "retrieve_low_priority_emails_for" for %s', email_address)
                    continue

                task_logger.info('syncing %s', email_address)

                retrieve_low_priority_emails_for.apply_async(
                    args=(email_account.id,),
                    max_retries=1,
                    default_retry_delay=100,
                    kwargs={'status_id': status.pk},
                )

            task_logger.info('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.info('synchronize scheduler already running')


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
        email_account = EmailAccount.objects.get(id=emailaccount_id)
    except EmailAccount.DoesNotExist:
        pass
    else:
        # Check for inactivity
        now_utc = datetime.now(tzutc())
        last_login_utc = CustomUser.objects.filter(tenant=email_account.tenant).order_by('-last_login').values_list('last_login')[0][0]

        activity_timedelta = now_utc - last_login_utc
        if activity_timedelta > timedelta(days=28):
            # Period of inactivity for two weeks: skip synchronize for this email account
            task_logger.info('%s inactive for 28 days',
                             email_account.email.email_address)
            return
        else:
            task_logger.info('%s last activity was %s ago',
                             email_account.email.email_address,
                             str(activity_timedelta))
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
                        modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE']
                        for folder in folders:
                            before = datetime.now()
                            synchronize_folder(
                                email_account,
                                server,
                                folder,
                                criteria=['SINCE "%s"' % datetime_since],
                                modifiers_new=modifiers_new,
                                new_only=True
                            )
                            task_logger.info('Retrieving new messages in folder %s list in %ss',
                                             folder,
                                             (datetime.now() - before).total_seconds())

                        # Download full messags from DRAFTS
                        modifiers_old = modifiers_new = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE']
                        synchronize_folder(
                            email_account,
                            server,
                            drafts_folder,
                            modifiers_old=modifiers_old,
                            modifiers_new=modifiers_new
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
        email_account = EmailAccount.objects.get(id=emailaccount_id)
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
                    modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE']
                    for folder in folders:
                        synchronize_folder(
                            email_account,
                            server,
                            folder,
                            criteria=['ALL'],
                            modifiers_new=modifiers_new,
                            new_only=True
                        )

                    modifiers_old = modifiers_new = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE']
                    synchronize_folder(
                        email_account,
                        server,
                        drafts_folder,
                        modifiers_old=modifiers_old,
                        modifiers_new=modifiers_new
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
            task_logger.info('synchronize scheduler starting')

            # Find email accounts which authentication info should be OK.
            email_accounts = EmailAccount.objects.filter(auth_ok__gt=NO_EMAILACCOUNT_AUTH).order_by('-last_sync_date')
            for email_account in email_accounts:
                email_address = email_account.email.email_address

                task_logger.info('attempting sync for %s', email_address)
                locked, status = lock_task('retrieve_all_flags_for', email_account.id)
                if not locked:
                    task_logger.info('skipping task "retrieve_all_flags_for" for %s', email_address)
                    continue

                task_logger.info('syncing %s', email_address)

                retrieve_all_flags_for.apply_async(
                    args=(email_account.id,),
                    max_retries=1,
                    default_retry_delay=100,
                    kwargs={'status_id': status.pk},
                )

            task_logger.info('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.info('synchronize scheduler already running')


@task(name='retrieve_all_flags_for', bind=True)
@monitor_task(logger=task_logger)
def retrieve_all_flags_for(emailaccount_id):
    """
    Download all FLAGS for emails via IMAP for an EmailAccount. This skips downloading
    the full body for e-mails but only updates the status UNSEEN, DELETED etc.
    """
    try:
        email_account = EmailAccount.objects.get(id=emailaccount_id)
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
                            modifiers_old=modifiers_old
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
            email_account = EmailAccount.objects.get(pk=account_id)
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
            email_account = EmailAccount.objects.get(pk=account_id)
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


@task(name='move_messages')
def move_messages(message_ids, to_folder_name):
    """
    Move n messages in the background.
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
            email_account = EmailAccount.objects.get(pk=account_id)
        except EmailAccount.DoesNotExist:
            pass
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
                        # TODO: warn user that move has failed
                    else:
                        # Delete local messages
                        EmailMessage.objects.filter(id__in=message_ids).delete()

                        # Synchronize with target_folder
                        synchronize_folder(email_account, server, target_folder, new_only=True)
                elif not server.auth_ok:
                    email_account.auth_ok = NO_EMAILACCOUNT_AUTH
                    email_account.save()


###
## HELPER METHODS
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
def synchronize_folder(account, server, folder, criteria=None, modifiers_old=None, modifiers_new=None, old_only=False, new_only=False):  # pylint: disable=R0913
    """
    Fetch and store modifiers_old for UIDs already in the database and
    modifiers_new for UIDs that only exist remotely.
    """
    criteria = criteria or ['ALL']
    modifiers_old = modifiers_old or ['FLAGS']
    modifiers_new = modifiers_new or ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE']

    # Process messages in batches to save memory
    messages_batch_size = 1000
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
                for i in range(0, len(known_uids), messages_batch_size):
                    folder_messages = server.get_messages(known_uids[i:i + messages_batch_size], modifiers_old, folder)
                    if len(folder_messages) > 0:
                        save_email_messages(folder_messages, account, folder, new_messages=False)
                    del folder_messages

        if not old_only:
            if len(new_uids):
                # Retrieve modifiers_new for new_uids
                for i in range(0, len(new_uids), messages_batch_size):
                    folder_messages = server.get_messages(new_uids[i:i + messages_batch_size], modifiers_new, folder)
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
    """
    task_logger.warn('Saving %s messages for %s in %s in the database', len(messages), account.email.email_address, folder.name_on_server)
    try:
        new_email_attachments = {}
        new_inline_email_attachments = {}
        update_email_attachments = {}
        update_inline_email_attachments = {}
        email_message_polymorphic_ctype = ContentType.objects.get_for_model(EmailMessage)

        if new_messages:
            task_logger.info('Saving these messages with the ORM since they are new')

            new_message_obj_list = []
            new_email_headers = {}
            new_email_address_headers = {}
            for message in messages:
                # Create get existing message or create a new one
                if message.get_sent_date() is not None:
                    sent_date = message.get_sent_date()
                else:
                    task_logger.warn('Emailmessage has no sent date, cannot create message')

                email_message, created = EmailMessage.objects.get_or_create(
                    uid=message.uid,
                    folder_name=folder.name_on_server,
                    account=account,
                    sent_date=sent_date,
                    tenant=account.tenant,
                )

                if message.get_flags() is not None:
                    email_message.is_seen = SEEN in message.get_flags()
                    email_message.flags = message.get_flags()

                body_html = message.get_html_body(remove_tags=settings.BLACKLISTED_EMAIL_TAGS)
                body_text = message.get_text_body()

                if body_html is not None and not body_text:
                    body_text = convert_html_to_text(body_html, keep_linebreaks=True)
                elif body_text is not None:
                    body_text = escape(body_text)

                # Check for headers
                if message.get_headers() is not None:
                    headers = message.get_headers()
                    # Remove certain headers that are stored in the model instead
                    if 'Received' in headers:
                        del headers['Received']
                    if 'Date' in headers:
                        del headers['Date']

                    email_headers = []
                    email_address_headers = []
                    for name, value in headers.items():
                        email_header = EmailHeader()
                        email_header.name = name
                        email_header.value = value
                        email_headers.append(email_header)
                        # For some headers we want to save it also in EmailAddressHeader model.
                        if name in ['To', 'From', 'CC', 'Delivered-To', 'Sender']:
                            email_addresses = getaddresses([value])
                            for address_name, email_address in email_addresses:  # pylint: disable=W0612
                                if email_address:
                                    email_address_header = EmailAddressHeader()
                                    email_address_header.name = name
                                    email_address_header.value = email_address.lower()
                                    email_address_headers.append(email_address_header)
                        elif name.lower() == 'message-id':
                            email_message.message_identifier = value
                    if len(email_headers):
                        # Save reference to uid
                        new_email_headers.update({message.uid: email_headers})
                    if len(email_address_headers):
                        # Save reference to uid
                        new_email_address_headers.update({message.uid: email_address_headers})

                email_message.body_html = replace_anchors_in_html(body_html)
                email_message.body_text = body_text
                email_message.size = message.get_size()
                email_message.folder_identifier = folder.identifier
                email_message.is_private = False
                email_message.tenant = account.tenant
                email_message.polymorphic_ctype = email_message_polymorphic_ctype
                # Add to object list
                new_message_obj_list.append(email_message)
                email_message.save()

                # Check for attachments
                email_attachments = []
                for attachment in message.get_attachments():
                    attachment_file = StringIO.StringIO(attachment.get('payload'))
                    attachment_file.content_type = attachment.get('content_type')
                    attachment_file.size = attachment.get('size')
                    attachment_file.name = attachment.get('name')

                    email_attachment = EmailAttachment()
                    email_attachment.attachment = attachment_file
                    email_attachment.size = attachment.get('size')
                    email_attachment.tenant = account.tenant
                    email_attachments.append(email_attachment)
                if len(email_attachments):
                    # Save reference to uid
                    new_email_attachments.update({message.uid: email_attachments})

                # Check for inline attachments
                inline_email_attachments = []
                for cid, attachment in message.get_inline_attachments().items():
                    attachment_file = StringIO.StringIO(attachment.get('payload'))
                    attachment_file.content_type = attachment.get('content_type')
                    attachment_file.size = attachment.get('size')
                    attachment_file.name = attachment.get('name')

                    inline_email_attachment = EmailAttachment()
                    inline_email_attachment.attachment = attachment_file
                    inline_email_attachment.size = attachment.get('size')
                    inline_email_attachment.tenant = account.tenant
                    inline_email_attachment.inline = True
                    inline_email_attachment.cid = cid
                    inline_email_attachments.append(inline_email_attachment)
                if len(inline_email_attachments):
                    # Save reference to uid
                    new_inline_email_attachments.update({message.uid: inline_email_attachments})

            # Save new_email_messages
            if len(new_message_obj_list):
                # Fetch message ids
                email_messages = EmailMessage.objects.filter(account=account, uid__in=[message.uid for message in messages], folder_name=folder.name_on_server).values_list('id', 'uid')

                # Link message ids to headers and (inline) attachments
                for id, uid in email_messages:
                    header_obj_list = new_email_headers.get(uid)
                    if header_obj_list:
                        for header_obj in header_obj_list:
                            header_obj.message_id = id

                    email_address_header_obj_list = new_email_address_headers.get(uid)
                    if email_address_header_obj_list:
                        for header_obj in email_address_header_obj_list:
                            header_obj.message_id = id

                    attachment_obj_list = new_email_attachments.get(uid)
                    if attachment_obj_list:
                        for attachment_obj in attachment_obj_list:
                            attachment_obj.message_id = id

                    inline_attachment_obj_list = new_inline_email_attachments.get(uid)
                    if inline_attachment_obj_list:
                        for attachment_obj in inline_attachment_obj_list:
                            attachment_obj.message_id = id

                # Save new_email_headers
                if len(new_email_headers):
                    new_header_obj_list = []
                    # Add header to object list
                    for uid, headers in new_email_headers.items():
                        for header in headers:
                            new_header_obj_list.append(header)

                    EmailHeader.objects.bulk_create(new_header_obj_list)

                # Save new_email_address_headers
                if len(new_email_address_headers):
                    new_email_address_header_obj_list = []
                    # Add header to object list
                    for uid, email_address_headers in new_email_address_headers.items():
                        for email_address_header in email_address_headers:
                            new_email_address_header_obj_list.append(email_address_header)

                    EmailAddressHeader.objects.bulk_create(new_email_address_header_obj_list)

        elif not new_messages:
            task_logger.info('Saving these messages with custom concatenated SQL since they need to be updated')

            # Build query string and parameter list
            total_query_string = ''
            param_list = []
            query_count = 0
            update_email_headers = {}
            update_email_address_headers = {}

            cursor = None
            if len(messages) > 0:
                cursor = connection.cursor()

            task_logger.info('Looping through %s messages', len(messages))
            for message in messages:
                query_string = 'UPDATE email_emailmessage SET is_deleted = FALSE, '
                if message.get_flags() is not None:
                    query_string += 'flags = %s, '
                    param_list.append(str(message.get_flags()))

                body_html = message.get_html_body(remove_tags=settings.BLACKLISTED_EMAIL_TAGS)
                body_text = message.get_text_body()

                if body_html is not None and not body_text:
                    body_text = convert_html_to_text(body_html, keep_linebreaks=True)

                if body_html is not None:
                    query_string += 'body_html = %s, '
                    param_list.append(replace_anchors_in_html(body_html))

                if body_text is not None:
                    query_string += 'body_text = %s, '
                    param_list.append(escape(body_text))

                if query_string.endswith(', '):
                    query_string = query_string.rstrip(', ')
                    query_string += ' WHERE account_id = %s AND uid = %s AND folder_name = %s;\n'
                    param_list.append(account.id)
                    param_list.append(message.uid)
                    param_list.append(folder.name_on_server)

                    total_query_string += query_string
                    query_count += 1

                if message.get_flags() is not None or message.get_sent_date() is not None:
                    query_string = 'UPDATE messaging_message SET '

                    if message.get_flags() is not None:
                        query_string += 'is_seen = %s, '
                        param_list.append(SEEN in message.get_flags())

                    if message.get_sent_date() is not None:
                        query_string += 'sent_date = %s, '
                        param_list.append(datetime.strftime(message.get_sent_date(), '%Y-%m-%d %H:%M:%S%z'))

                    query_string = query_string.rstrip(', ')
                    query_string += ' WHERE historylistitem_ptr_id = (SELECT message_ptr_id FROM email_emailmessage WHERE account_id = %s AND uid = %s AND folder_name = %s);\n'
                    param_list.append(account.id)
                    param_list.append(message.uid)
                    param_list.append(folder.name_on_server)

                    total_query_string += query_string
                    query_count += 1

                # Check for headers
                if message.get_headers() is not None:
                    headers = message.get_headers()

                    # Remove certain headers that are stored in the model instead
                    if 'Received' in headers:
                        del headers['Received']
                    if 'Date' in headers:
                        del headers['Date']

                    email_headers = []
                    email_address_headers = []
                    for name, value in headers.items():
                        email_header = EmailHeader()
                        email_header.name = name
                        email_header.value = value
                        email_headers.append(email_header)
                        # For some headers we want to save it also in EmailAddressHeader model.
                        if name in ['To', 'From', 'CC', 'Delivered-To', 'Sender']:
                            email_addresses = getaddresses([value])
                            for address_name, email_address in email_addresses:
                                if email_address:
                                    email_address_header = EmailAddressHeader()
                                    email_address_header.name = name
                                    email_address_header.value = email_address.lower()
                                    email_address_headers.append(email_address_header)
                    if len(email_headers):
                        # Save reference to uid
                        update_email_headers.update({message.uid: email_headers})
                    if len(email_address_headers):
                        # Save reference to uid
                        update_email_address_headers.update({message.uid: email_address_headers})

                # Check for attachments
                email_attachments = []
                for attachment in message.get_attachments():
                    attachment_file = StringIO.StringIO(attachment.get('payload'))
                    attachment_file.content_type = attachment.get('content_type')
                    attachment_file.size = attachment.get('size')
                    attachment_file.name = attachment.get('name')

                    email_attachment = EmailAttachment()
                    email_attachment.attachment = attachment_file
                    email_attachment.size = attachment.get('size')
                    email_attachment.tenant = account.tenant
                    email_attachments.append(email_attachment)
                if len(email_attachments):
                    # Save reference to uid
                    update_email_attachments.update({message.uid: email_attachments})

                # Check for inline attachments
                inline_email_attachments = []
                for cid, attachment in message.get_inline_attachments().items():
                    attachment_file = StringIO.StringIO(attachment.get('payload'))
                    attachment_file.content_type = attachment.get('content_type')
                    attachment_file.size = attachment.get('size')
                    attachment_file.name = attachment.get('name')

                    inline_email_attachment = EmailAttachment()
                    inline_email_attachment.attachment = attachment_file
                    inline_email_attachment.size = attachment.get('size')
                    inline_email_attachment.tenant = account.tenant
                    inline_email_attachment.inline = True
                    inline_email_attachment.cid = cid
                    inline_email_attachments.append(inline_email_attachment)

                if len(inline_email_attachments):
                    # Save reference to uid
                    update_inline_email_attachments.update({message.uid: inline_email_attachments})

            # Execute queries
            if query_count:
                task_logger.info('Executing (%s) queries for e-mail messages', query_count)
                cursor.execute(total_query_string, param_list)

                # reset counter and query variables
                query_count = 0
                total_query_string = ''
                param_list = []

            # Fetch message ids
            email_message_uids = EmailMessage.objects.filter(account=account, uid__in=[message.uid for message in messages], folder_name=folder.name_on_server).values_list('id', 'uid')

            # Find existing headers per email message
            existing_headers_per_message = {}
            existing_headers_qs = EmailHeader.objects.filter(message_id__in=[id for id, uid in email_message_uids]).values_list('message_id', 'name')
            for message_id, header_name in existing_headers_qs:
                headers = existing_headers_per_message.get(message_id, [])
                headers.append(header_name)
                existing_headers_per_message.update({message_id: headers})

            # Find existing email address headers per email message
            existing_email_address_headers_per_message = {}
            existing_email_address_headers_qs = EmailAddressHeader.objects.filter(message_id__in=[id for id, uid in email_message_uids]).values_list('message_id', 'name')
            for message_id, header_name in existing_email_address_headers_qs:
                headers = existing_email_address_headers_per_message.get(message_id, [])
                headers.append(header_name)
                existing_email_address_headers_per_message.update({message_id: headers})

            # Link message ids to headers and (inline) attachments
            for id, uid in email_message_uids:
                header_obj_list = update_email_headers.get(uid)
                if header_obj_list:
                    for header_obj in header_obj_list:
                        header_obj.message_id = id

                email_address_header_obj_list = update_email_address_headers.get(uid)
                if email_address_header_obj_list:
                    for header_obj in email_address_header_obj_list:
                        header_obj.message_id = id

                attachment_obj_list = update_email_attachments.get(uid)
                if attachment_obj_list:
                    for attachment_obj in attachment_obj_list:
                        attachment_obj.message_id = id

                inline_attachment_obj_list = update_inline_email_attachments.get(uid)
                if inline_attachment_obj_list:
                    for attachment_obj in inline_attachment_obj_list:
                        attachment_obj.message_id = id

            # Save update_email_headers
            if len(update_email_headers):
                update_header_obj_list = []
                # Add header to object list
                for uid, headers in update_email_headers.items():
                    for header in headers:
                        update_header_obj_list.append(header)

                # Build query string and parameter list
                total_query_string = ''
                param_list = []
                query_count = 0
                task_logger.info('Looping through %s headers that need updating', len(update_header_obj_list))
                for header_obj in update_header_obj_list:
                    # Decide whether to update or insert this email header
                    if header_obj.name in existing_headers_per_message.get(header_obj.message_id, []):
                        # Update email header
                        query_string = 'UPDATE email_emailheader SET '
                        query_string += 'value = %s '

                        query_string += 'WHERE name = %s AND message_id = %s;\n'
                        param_list.append(header_obj.value)
                        param_list.append(header_obj.name)
                        param_list.append(header_obj.message_id)
                    else:
                        # Insert email header
                        query_string = 'INSERT INTO email_emailheader (name, value, message_id) VALUES (%s, %s, %s);\n'
                        param_list.append(header_obj.name)
                        param_list.append(header_obj.value)
                        param_list.append(header_obj.message_id)

                    total_query_string += query_string
                    query_count += 1

                # Execute queries
                if query_count:
                    task_logger.info('Executing (%s) queries for e-mail headers', query_count)
                    cursor.execute(total_query_string, param_list)

                    # reset counter and query variables
                    query_count = 0
                    total_query_string = ''
                    param_list = []

                else:
                    task_logger.info('No queries to execute')
            if cursor:
                cursor.close()

            # Save update_email_address_headers
            if len(update_email_address_headers):
                update_email_address_header_obj_list = []
                for uid, headers in update_email_address_headers.items():
                    # Add header to object list
                    for header in headers:
                        update_email_address_header_obj_list.append(header)

                # Build query string and parameter list
                total_query_string = ''
                param_list = []
                query_count = 0
                task_logger.info('Looping through %s email headers that need updating', len(update_email_address_header_obj_list))
                for header_obj in update_email_address_header_obj_list:
                    # Decide whether to update or insert this email header
                    if header_obj.name in existing_headers_per_message.get(header_obj.message_id, []):
                        # Update email header
                        query_string = 'UPDATE email_emailaddressheader SET '
                        query_string += 'value = %s '

                        query_string += 'WHERE name = %s AND message_id = %s;\n'
                        param_list.append(header_obj.value)
                        param_list.append(header_obj.name)
                        param_list.append(header_obj.message_id)
                    else:
                        # Insert email header
                        query_string = 'INSERT INTO email_emailaddressheader (name, value, message_id) VALUES (%s, %s, %s);\n'
                        param_list.append(header_obj.name)
                        param_list.append(header_obj.value)
                        param_list.append(header_obj.message_id)

                    total_query_string += query_string
                    query_count += 1

                # Execute queries
                if query_count:
                    task_logger.info('Executing (%s) queries for e-mailaddress headers', query_count)
                    cursor = connection.cursor()
                    cursor.execute(total_query_string, param_list)

                    # reset counter and query variables
                    query_count = 0
                    total_query_string = ''
                    param_list = []
                else:
                    task_logger.info('No queries to execute')

        # Save attachments for new messages
        for uid, attachment_list in new_email_attachments.items():
            for attachment in attachment_list:
                attachment.attachment = File(attachment.attachment, attachment.attachment.name)

                # Upload attachments that are new or if it belongs to a draft
                path = get_attachment_upload_path(attachment, attachment.attachment.name)
                if not default_storage.exists(path) or folder.identifier == DRAFTS:
                    attachment.save()
                else:
                    attachment.attachment.name = path

        # Save inline attachments for new messages
        for uid, attachment_list in new_inline_email_attachments.items():
            cid_attachments = {}
            for attachment in attachment_list:
                attachment.attachment = File(attachment.attachment, attachment.attachment.name)

                path = get_attachment_upload_path(attachment, attachment.attachment.name)
                email_attachment, created = EmailAttachment.objects.get_or_create(inline=True, size=attachment.size, message_id=attachment.message_id, tenant_id=account.tenant_id)
                email_attachment.attachment = attachment.attachment
                email_attachment.save()

                cid_attachments[attachment.cid] = email_attachment

            if len(attachment_list) > 0:
                # Replace img elements with the *cid* src attribute to they point to AWS
                email_message = attachment_list[0].message
                email_message.body_html = replace_cid_in_html(email_message.body_html, cid_attachments)
                email_message.save()

        # Save attachments for updated messages
        for uid, attachment_list in update_email_attachments.items():
            for attachment in attachment_list:
                attachment.attachment = File(attachment.attachment, attachment.attachment.name)

                # Upload attachments that are new or if it belongs to a draft
                path = get_attachment_upload_path(attachment, attachment.attachment.name)
                if not default_storage.exists(path) or folder.identifier == DRAFTS:
                    attachment.save()
                else:
                    attachment.attachment.name = path

        # Save inline attachments for updated messages
        for uid, attachment_list in update_inline_email_attachments.items():
            cid_attachments = {}
            for attachment in attachment_list:
                attachment.attachment = File(attachment.attachment, attachment.attachment.name)

                # Upload attachments that are new or if it belongs to a draft
                path = get_attachment_upload_path(attachment, attachment.attachment.name)
                email_attachment, created = EmailAttachment.objects.get_or_create(inline=True, attachment=path, size=attachment.size, message_id=attachment.message_id, tenant_id=account.tenant_id)
                email_attachment.attachment = attachment.attachment
                if created and not default_storage.exists(path) or folder.identifier == DRAFTS:
                    email_attachment.save()
                else:
                    attachment.attachment.name = path

                cid_attachments[attachment.cid] = email_attachment

            if len(attachment_list) > 0 and len(cid_attachments) > 0:
                # Replace img elements with the *cid* src attribute to they point to AWS
                email_message = attachment_list[0].message
                email_message.body_html = replace_cid_in_html(email_message.body_html, cid_attachments)
                email_message.save()

    except Exception, e:  # pylint: disable=W0703
        print traceback.format_exc(e)
    finally:
        # Let garbage collection do it's job
        messages = None
        update_email_headers = None
        update_header_obj_list = None
        param_list = None
        email_messages = None
        existing_headers_qs = None
        new_message_obj_list = None

        gc.collect()

    task_logger.info('Messages saved')


def _task_prerun_listener(**kwargs):
    """
    Because of a threading issue in the Crypto library (which seems to be intentional),
    we need to call the atfork function to sync the worker with it's PID.

    When this is not done we get exceptions during decryption of email username/password.
    """
    Random.atfork()
task_prerun.connect(_task_prerun_listener)

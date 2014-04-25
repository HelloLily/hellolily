from __future__ import absolute_import
import logging
import StringIO
import traceback
from datetime import datetime, timedelta
from Crypto import Random

from celery import task
from celery.signals import task_prerun
from dateutil.tz import tzutc
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.utils.html import escape
from imapclient import SEEN, DELETED
from python_imap.folder import ALLMAIL, DRAFTS, TRASH, INBOX, SENT
from python_imap.server import IMAP, CATCH_LOGIN_ERRORS
from python_imap.utils import convert_html_to_text

from lily.messaging.email.models import EmailAccount, EmailMessage, EmailHeader, EmailAttachment, OK_EMAILACCOUNT_AUTH, NO_EMAILACCOUNT_AUTH
from lily.messaging.email.utils import get_attachment_upload_path, replace_anchors_in_html, replace_cid_in_html, get_task_count
from lily.users.models import CustomUser

# while profiling
import resource


task_logger = logging.getLogger('celery_task')

LOCK_EXPIRE = 300  # lock expire in seconds
# cache.add failes if the key already exists
acquire_lock = lambda (lock_id): cache.add(lock_id, "true", LOCK_EXPIRE)
release_lock = lambda (lock_id): cache.delete(lock_id)


@task(name='synchronize_email_scheduler')
def synchronize_email_scheduler():
    """
    Attempt to start a new task for every active mailbox to synchronize
    via IMAP.
    """
    lock_id = 'synchronize_email_scheduler'

    if acquire_lock(lock_id):  # this should always work, but just in case..
        try:
            task_logger.info('synchronize scheduler starting')

            emailaccounts = EmailAccount.objects.filter(auth_ok__gt=NO_EMAILACCOUNT_AUTH).order_by('-last_sync_date')
            for emailaccount in emailaccounts:
                emailaccount_id = emailaccount.id
                email_address = emailaccount.email.email_address

                task_logger.info('attempting sync for %s', email_address)

                retrieve_all_emails_task_count = get_task_count('retrieve_all_emails_for', ['scheduled', 'reserved'], arguments=u'[%d]' % emailaccount_id)
                retrieve_new_emails_task_count = get_task_count('retrieve_new_emails_for', ['scheduled', 'reserved'], arguments=u'[%d]' % emailaccount_id)
                in_a_moment = datetime.now(tzutc()) + timedelta(seconds=10)

                if not emailaccount.last_sync_date:
                    if retrieve_all_emails_task_count == 0:
                        retrieve_all_emails_for.apply_async(
                            args=(emailaccount_id,),
                            eta=in_a_moment
                        )
                    else:
                        task_logger.info('skipping task "retrieve_all_emails_for" for %s', email_address)
                else:
                    if retrieve_new_emails_task_count == 0:
                        retrieve_new_emails_for.apply_async(
                            args=(emailaccount_id,),
                            eta=in_a_moment
                        )
                    else:
                        task_logger.info('skipping task "retrieve_new_emails_for" for %s', email_address)

            task_logger.info('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.info('synchronize scheduler already running')


@task(name='retrieve_new_emails_for')
def retrieve_new_emails_for(emailaccount_id):
    """
    Download new emails via IMAP for an EmailAccount since
     *last_sync_date* unless there has been some period of inactivity.
    A period of inactivity is considered when:
        - the users that can access the emailaccount have not logged in
          for 4 weeks (if the emailaccount is owned by a user)
        - there is no user for that tenant who logged in for
          4 weeks (if the emailaccount is not owned by a user, but
          by a normal contact/account)
    """
    try:
        emailaccount = EmailAccount.objects.get(id=emailaccount_id)
    except EmailAccount.DoesNotExist:
        pass
    else:
        lock_id = 'EmailAccount(%d)' % emailaccount_id

        if acquire_lock(lock_id):
            try:
                # Check for inactivity
                now_utc = datetime.now(tzutc())
                last_login_utc = CustomUser.objects.filter(tenant=emailaccount.tenant).order_by('-last_login').values_list('last_login')[0][0]

                activity_timedelta = now_utc - last_login_utc
                if activity_timedelta > timedelta(days=28):
                    # Period of inactivity for two weeks: skip synchronize for this emailaccount
                    task_logger.info('%s inactive for 28 days', emailaccount.email.email_address)
                    return
                else:
                    task_logger.info('%s last activity was %s ago', emailaccount.email.email_address, str(activity_timedelta))

                    # Download new messages since last synchronization if that was some time ago
                    last_sync_date = emailaccount.last_sync_date
                    if not last_sync_date:
                        last_sync_date = datetime.fromtimestamp(0)
                    last_sync_date_utc = last_sync_date.astimezone(tzutc())
                    task_logger.info('last synchronization for %s happened at %s', emailaccount.email.email_address, last_sync_date_utc)
                    if now_utc - last_sync_date_utc > timedelta(minutes=5):
                        task_logger.info('start synchronizing folders for %s', emailaccount.email.email_address)
                        datetime_since = last_sync_date.strftime('%d-%b-%Y %H:%M:%S')

                        server = None
                        try:
                            host = emailaccount.provider.imap_host
                            port = emailaccount.provider.imap_port
                            ssl = emailaccount.provider.imap_ssl
                            server = IMAP(host, port, ssl)

                            if server.login(emailaccount.username, emailaccount.password):
                                emailaccount.auth_ok = OK_EMAILACCOUNT_AUTH

                                # Update folder list
                                before = datetime.now()
                                emailaccount.folders = get_account_folders_from_server(server)
                                task_logger.info('Retrieving IMAP folder list for %s in %ss', emailaccount.email.email_address, (datetime.now() - before).total_seconds())

                                # Download full email messages from INBOX
                                modifiers_new = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                                criteria = ['UNSEEN SINCE "%s"' % datetime_since]
                                folders = [server.get_folder(INBOX)]
                                for folder in folders:
                                    before = datetime.now()
                                    synchronize_folder(emailaccount, server, folder, criteria=criteria, modifiers_new=modifiers_new, new_only=True)
                                    task_logger.info('Retrieving new messages in folder %s list since %s in %ss', folder, datetime_since, (datetime.now() - before).total_seconds())

                                # Download email headers from messages in ALLMAIL
                                modifiers_old = modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                                criteria = ['SINCE "%s"' % datetime_since]
                                folder = server.get_folder(ALLMAIL)
                                before = datetime.now()
                                synchronize_folder(emailaccount, server, folder, criteria=criteria, modifiers_old=modifiers_old, modifiers_new=modifiers_new)
                                task_logger.info('Retrieving new messages in folder %s since %s list in %ss', folder, datetime_since, (datetime.now() - before).total_seconds())

                                emailaccount.last_sync_date = now_utc
                            else:
                                task_logger.info('IMAP login failed for %s', emailaccount.email.email_address)
                                if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                                    emailaccount.auth_ok = NO_EMAILACCOUNT_AUTH
                            emailaccount.save()
                        finally:
                            if server:
                                server.logout()

            finally:
                release_lock(lock_id)


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

            emailaccounts = EmailAccount.objects.filter(auth_ok__gt=NO_EMAILACCOUNT_AUTH).order_by('-last_sync_date')
            for emailaccount in emailaccounts:
                emailaccount_id = emailaccount.id
                email_address = emailaccount.email.email_address

                task_logger.info('attempting sync for %s', email_address)

                retrieve_low_priority_task_count = get_task_count('retrieve_low_priority_emails_for', ['scheduled', 'reserved'], arguments=u'[%d]' % emailaccount_id)
                if retrieve_low_priority_task_count == 0:
                    in_a_moment = datetime.now(tzutc()) + timedelta(seconds=10)
                    retrieve_low_priority_emails_for.apply_async(
                        args=(emailaccount_id,),
                        eta=in_a_moment
                    )
                else:
                    task_logger.info('skipping task "retrieve_low_priority_emails_for" for %s', email_address)

            task_logger.info('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.info('synchronize scheduler already running')


@task(name='retrieve_low_priority_emails_for')
def retrieve_low_priority_emails_for(emailaccount_id):
    """
    Download emails via IMAP for an EmailAccount for other folders than INBOX
    unless there has been some period of inactivity.
    A period of inactivity is considered when:
        - the users that can access the emailaccount have not logged in
          for 4 weeks (if the emailaccount is owned by a user)
        - there is no user for that tenant who logged in for
          4 weeks (if the emailaccount is not owned by a user, but
          by a normal contact/account)
    The downloaded emails are 47h59s old at max.
    """
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    task_logger.warn('rusage in retrieve_low_priority_emails_for --START-- Memory usage: %d', rusage.ru_maxrss)
    try:
        emailaccount = EmailAccount.objects.get(id=emailaccount_id)
    except EmailAccount.DoesNotExist:
        pass
    else:
        lock_id = 'EmailAccount(%d)' % emailaccount_id

        if acquire_lock(lock_id):
            try:
                # Check for inactivity
                now_utc = datetime.now(tzutc())
                last_login_utc = CustomUser.objects.filter(tenant=emailaccount.tenant).order_by('-last_login').values_list('last_login')[0][0]

                activity_timedelta = now_utc - last_login_utc
                if activity_timedelta > timedelta(days=28):
                    # Period of inactivity for two weeks: skip synchronize for this emailaccount
                    task_logger.info('%s inactive for 28 days', emailaccount.email.email_address)
                    return
                else:
                    task_logger.info('%s last activity was %s ago', emailaccount.email.email_address, str(activity_timedelta))
                    last_sync_date = emailaccount.last_sync_date
                    if not last_sync_date:
                        last_sync_date = datetime.fromtimestamp(0)
                    last_sync_date_utc = last_sync_date.astimezone(tzutc())
                    last_sync_date_utc -= timedelta(days=1)
                    datetime_since = last_sync_date_utc.strftime('%d-%b-%Y 00:00:00')

                    server = None
                    try:
                        host = emailaccount.provider.imap_host
                        port = emailaccount.provider.imap_port
                        ssl = emailaccount.provider.imap_ssl
                        server = IMAP(host, port, ssl)

                        if server.login(emailaccount.username, emailaccount.password):
                            emailaccount.auth_ok = OK_EMAILACCOUNT_AUTH

                            # Update folder list
                            emailaccount.folders = get_account_folders_from_server(server)

                            # Download email headers from messages in all folders except INBOX, DRAFTS, ALLMAIL
                            modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                            folders = server.get_folders(exclude=[DRAFTS])
                            for folder in folders:
                                task_logger.warn('rusage in retrieve_low_priority_emails_for --BETWEEN-- Memory usage: %d', rusage.ru_maxrss)
                                before = datetime.now()
                                synchronize_folder(emailaccount, server, folder, criteria=['SINCE "%s"' % datetime_since], modifiers_new=modifiers_new, new_only=True)
                                task_logger.info('Retrieving new messages in folder %s list in %ss', folder, (datetime.now() - before).total_seconds())

                            # Download full messags from DRAFTS
                            task_logger.warn('rusage in retrieve_low_priority_emails_for --BETWEEN-- Memory usage: %d', rusage.ru_maxrss)
                            modifiers_old = modifiers_new = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                            synchronize_folder(emailaccount, server, server.get_folder(DRAFTS), modifiers_old=modifiers_old, modifiers_new=modifiers_new)
                        else:
                            task_logger.info('IMAP login failed for %s', emailaccount.email.email_address)
                            if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                                emailaccount.auth_ok = NO_EMAILACCOUNT_AUTH
                        emailaccount.save()
                    finally:
                        if server:
                            server.logout()
            finally:
                release_lock(lock_id)
    task_logger.warn('rusage in retrieve_low_priority_emails_for --END-- Memory usage: %d', rusage.ru_maxrss)


@task(name='retrieve_all_emails_for')
def retrieve_all_emails_for(emailaccount_id):
    """
    Download all emails via IMAP for an EmailAccount. This skips downloading
    the full body for e-mails.
    """
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    task_logger.warn('rusage in retrieve_all_emails_for --START-- Memory usage: %d', rusage.ru_maxrss)
    try:
        emailaccount = EmailAccount.objects.get(id=emailaccount_id)
    except EmailAccount.DoesNotExist:
        pass
    else:
        lock_id = 'EmailAccount(%d)' % emailaccount_id

        if acquire_lock(lock_id):
            try:
                now_utc = datetime.now(tzutc())
                server = None
                try:
                    host = emailaccount.provider.imap_host
                    port = emailaccount.provider.imap_port
                    ssl = emailaccount.provider.imap_ssl
                    server = IMAP(host, port, ssl)

                    if server.login(emailaccount.username, emailaccount.password):
                        emailaccount.auth_ok = OK_EMAILACCOUNT_AUTH

                        # Update folder list
                        emailaccount.folders = get_account_folders_from_server(server)

                        modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                        folders = server.get_folders(exclude=[DRAFTS])
                        for folder in folders:
                            task_logger.warn('rusage in retrieve_all_emails_for --BETWEEN-- Memory usage: %d', rusage.ru_maxrss)
                            synchronize_folder(emailaccount, server, folder, criteria=['ALL'], modifiers_new=modifiers_new, new_only=True)

                        task_logger.warn('rusage in retrieve_all_emails_for --BETWEEN-- Memory usage: %d', rusage.ru_maxrss)
                        modifiers_old = modifiers_new = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']
                        synchronize_folder(emailaccount, server, server.get_folder(DRAFTS), modifiers_old=modifiers_old, modifiers_new=modifiers_new)

                        emailaccount.last_sync_date = now_utc
                    else:
                        task_logger.info('IMAP login failed for %s', emailaccount.email.email_address)
                        if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                            emailaccount.auth_ok = NO_EMAILACCOUNT_AUTH
                    emailaccount.save()
                finally:
                    if server:
                        server.logout()

            finally:
                release_lock(lock_id)
    task_logger.warn('rusage in retrieve_all_emails_for --END-- Memory usage: %d', rusage.ru_maxrss)


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

            emailaccounts = EmailAccount.objects.filter(auth_ok__gt=NO_EMAILACCOUNT_AUTH).order_by('-last_sync_date')
            for emailaccount in emailaccounts:
                emailaccount_id = emailaccount.id
                email_address = emailaccount.email.email_address

                task_logger.info('attempting sync for %s', email_address)

                retrieve_all_flags_task_count = get_task_count('retrieve_all_flags_for', ['scheduled', 'reserved'], arguments=u'[%d]' % emailaccount_id)
                if retrieve_all_flags_task_count == 0:
                    in_a_moment = datetime.now(tzutc()) + timedelta(seconds=10)
                    retrieve_all_flags_for.apply_async(
                        args=(emailaccount_id,),
                        eta=in_a_moment
                    )
                else:
                    task_logger.info('skipping task "retrieve_all_flags_for" for %s', email_address)

            task_logger.info('synchronize scheduler finished')
        finally:
            release_lock(lock_id)
    else:
        task_logger.info('synchronize scheduler already running')


@task(name='retrieve_all_flags_for')
def retrieve_all_flags_for(emailaccount_id):
    """
    Download all FLAGS for emails via IMAP for an EmailAccount. This skips downloading
    the full body for e-mails but only updates the status UNSEEN, DELETED etc.
    """
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    task_logger.warn('rusage in retrieve_all_flags_for --START-- Memory usage: %d', rusage.ru_maxrss)
    try:
        emailaccount = EmailAccount.objects.get(id=emailaccount_id)
    except EmailAccount.DoesNotExist:
        pass
    else:
        lock_id = 'EmailAccount(%d)-flags' % emailaccount_id

        if acquire_lock(lock_id):
            try:
                server = None
                try:
                    host = emailaccount.provider.imap_host
                    port = emailaccount.provider.imap_port
                    ssl = emailaccount.provider.imap_ssl
                    server = IMAP(host, port, ssl)

                    if server.login(emailaccount.username, emailaccount.password):
                        emailaccount.auth_ok = OK_EMAILACCOUNT_AUTH

                        # Update folder list
                        emailaccount.folders = get_account_folders_from_server(server)

                        modifiers_old = ['FLAGS', 'INTERNALDATE']
                        folders = server.get_folders(exclude=[DRAFTS, TRASH, SENT])
                        for folder in folders:
                            task_logger.warn('rusage in retrieve_all_flags_for --BETWEEN-- Memory usage: %d', rusage.ru_maxrss)
                            # synchronize_folder(emailaccount, server, folder, criteria=['ALL'], modifiers_old=modifiers_old, old_only=True)
                            synchronize_folder(emailaccount, server, folder, criteria=['ALL'], modifiers_old=modifiers_old)
                    else:
                        task_logger.warn('IMAP login failed for %s', emailaccount.email.email_address)
                        if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                            emailaccount.auth_ok = NO_EMAILACCOUNT_AUTH
                    emailaccount.save()
                finally:
                    if server:
                        server.logout()

            finally:
                release_lock(lock_id)
    task_logger.warn('rusage in retrieve_all_flags_for --END-- Memory usage: %d', rusage.ru_maxrss)


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

    # Mark in database first for immediate effect
    EmailMessage.objects.filter(id__in=message_ids).update(is_seen=read)

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
        account_qs = EmailAccount.objects.filter(pk=account_id)
        if len(account_qs) > 0:
            account = account_qs[0]
            server = None
            try:
                host = account.provider.imap_host
                port = account.provider.imap_port
                ssl = account.provider.imap_ssl
                server = IMAP(host, port, ssl)

                if server.login(account.username, account.password):
                    account.auth_ok = OK_EMAILACCOUNT_AUTH

                    for folder_name, uids in folders.items():
                        folder = server.get_folder(folder_name)
                        is_selected, select_info = server.select_folder(folder.get_search_name(), readonly=False)

                        if is_selected:
                            uids = ','.join([str(val) for val in uids])

                            if read:
                                server.client.add_flags(uids, [SEEN])
                            else:
                                server.client.remove_flags(uids, [SEEN])

                            server.client.close_folder()
                else:
                    task_logger.info('IMAP login failed for %s', account.email.email_address)
                    if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                        account.auth_ok = NO_EMAILACCOUNT_AUTH
                account.save()

            finally:
                if server:
                    server.logout()


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
        account_qs = EmailAccount.objects.filter(pk=account_id)
        if len(account_qs) > 0:
            account = account_qs[0]
            server = None
            try:
                host = account.provider.imap_host
                port = account.provider.imap_port
                ssl = account.provider.imap_ssl
                server = IMAP(host, port, ssl)

                if server.login(account.username, account.password):
                    account.auth_ok = OK_EMAILACCOUNT_AUTH

                    for folder_name, uids in folders.items():
                        folder = server.get_folder(folder_name)
                        is_selected, select_info = server.select_folder(folder.get_search_name(), readonly=False)

                        if is_selected:
                            uids = ','.join([str(val) for val in uids])

                            server.client.add_flags(uids, DELETED)

                            server.client.close_folder()
                else:
                    task_logger.info('IMAP login failed for %s', account.email.email_address)
                    if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                        account.auth_ok = NO_EMAILACCOUNT_AUTH
                account.save()
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                if server:
                    server.logout()


@task(name='move_messages')
def move_messages(message_ids, target_folder_name):
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
        account_qs = EmailAccount.objects.filter(pk=account_id)
        if len(account_qs) > 0:
            account = account_qs[0]
            server = None
            try:
                host = account.provider.imap_host
                port = account.provider.imap_port
                ssl = account.provider.imap_ssl
                server = IMAP(host, port, ssl)

                if server.login(account.username, account.password):
                    account.auth_ok = OK_EMAILACCOUNT_AUTH

                    # Get or create folder *target_folder_name*
                    target_folder = server.get_folder(target_folder_name)
                    if target_folder is None:
                        # Update folders for account
                        server.client.create_folder(target_folder_name)
                        account.folders = get_account_folders_from_server(server)

                        target_folder = server.get_folder(target_folder_name)

                    task_logger.info('target_folder.server_name %s', target_folder.name_on_server)

                    # Copy messages from origin folders to *target_folder*
                    for folder_name, uids in folders.items():
                        origin_folder = server.get_folder(folder_name)
                        is_selected, select_info = server.select_folder(origin_folder.get_search_name(), readonly=False)

                        if is_selected:
                            task_logger.info('in folder %s', origin_folder.get_search_name())
                            server.client.copy(uids, target_folder.get_search_name())

                            # Delete from origin folder remote
                            uids = ','.join([str(val) for val in uids])
                            server.client.add_flags(uids, DELETED)
                            server.client.close_folder()

                            # Delete from origin folder locally
                            EmailMessage.objects.filter(id__in=message_ids).delete()

                        # Synchronize with target_folder
                        synchronize_folder(account, server, target_folder, new_only=True)
                else:
                    task_logger.info('IMAP login failed for %s', account.email.email_address)
                    if server._login_failed_reason != CATCH_LOGIN_ERRORS[1]:
                        account.auth_ok = NO_EMAILACCOUNT_AUTH
                account.save()
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                if server:
                    server.logout()


###
## HELPER METHODS
###

def get_account_folders_from_server(server):
    """
    Map folders existing on *server* in a format that is used in template rendering.
    """
    account_folders = {}

    all_folders = server.get_folders(cant_select=True)
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
def synchronize_folder(account, server, folder, criteria=['ALL'], modifiers_old=['FLAGS', 'INTERNALDATE'], modifiers_new=['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To Cc Bcc Delivered-To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE'], old_only=False, new_only=False):
    """
    Fetch and store modifiers_old for UIDs already in the database and
    modifiers_new for UIDs that only exist remotely.
    """
    task_logger.debug('sync start for %s', unicode(folder.get_name()))

    # Find already known uids
    known_uids_qs = EmailMessage.objects.filter(account=account, folder_name=folder.name_on_server)
    if 'SEEN' in criteria:
        known_uids_qs = known_uids_qs.filter(is_seen=True)

    if 'UNSEEN' in criteria:
        known_uids_qs = known_uids_qs.filter(is_seen=False)

    known_uids = set(known_uids_qs.values_list('uid', flat=True))

    try:
        folder_count, remote_uids = server.get_uids(folder, criteria)

        # Get the difference between local and server uids
        new_uids = list(set(remote_uids).difference(known_uids))

        if not new_only:
            # UIDs that no longer exist in this folder
            removed_uids = list(known_uids.difference(set(remote_uids)))

            # Delete removed_uids from known_uids
            [known_uids.discard(x) for x in removed_uids]
            known_uids = list(known_uids)

            # Delete from database
            EmailMessage.objects.filter(account=account, folder_name=folder.name_on_server, uid__in=removed_uids).delete()

            if len(known_uids):
                # Renew modifiers_old for known_uids, TODO; check scenario where local_uids[x] has been moved/trashed
                folder_messages = server.get_messages(known_uids, modifiers_old, folder)

                if len(folder_messages) > 0:
                    save_email_messages(folder_messages, account, folder)

        if not old_only:
            if len(new_uids):
                # Retrieve modifiers_new for new_uids
                folder_messages = server.get_messages(new_uids, modifiers_new, folder)

                if len(folder_messages) > 0:
                    save_email_messages(folder_messages, account, folder, new_messages=True)

    except Exception, e:
        print traceback.format_exc(e)

    task_logger.debug('sync done for %s', unicode(folder.get_name()))


@transaction.commit_on_success
def save_email_messages(messages, account, folder, new_messages=False):
    """
    Save messages in database for account. Folder_name needs to be the server name.
    """
    task_logger.warn('Saving %s messages for %s in %s in the database', len(messages), account.email.email_address, folder.name_on_server)
    try:
        query_batch_size = 10000
        new_email_attachments = {}
        new_inline_email_attachments = {}
        update_email_attachments = {}
        update_inline_email_attachments = {}

        if new_messages:
            task_logger.info('Saving these messages with the ORM since they are new')

            new_message_obj_list = []
            new_email_headers = {}
            for message in messages:
                # Create new object
                email_message = EmailMessage()
                if message.get_sent_date() is not None:
                    email_message.sent_date = message.get_sent_date()
                email_message.account = account

                email_message.uid = message.uid
                if message.get_flags() is not None:
                    email_message.is_seen = SEEN in message.get_flags()
                    email_message.flags = message.get_flags()

                body_html = message.get_html_body()
                body_text = message.get_text_body()

                if body_html is not None and not body_text:
                    body_text = convert_html_to_text(body_html, keep_linebreaks=True)
                elif body_text is not None:
                    body_text = escape(body_text)

                email_message.body_html = replace_anchors_in_html(body_html)
                email_message.body_text = body_text
                email_message.size = message.get_size()
                email_message.folder_name = folder.name_on_server
                email_message.folder_identifier = folder.identifier
                email_message.is_private = False
                email_message.tenant = account.tenant
                email_message.polymorphic_ctype = ContentType.objects.get_for_model(EmailMessage)
                # Add to object list
                new_message_obj_list.append(email_message)
                email_message.save()

                # Check for headers
                if message.get_headers() is not None:
                    headers = message.get_headers()
                    # Remove certain headers that are stored in the model instead
                    if 'Received' in headers:
                        del headers['Received']
                    if 'Date' in headers:
                        del headers['Date']

                    email_headers = []
                    for name, value in headers.items():
                        email_header = EmailHeader()
                        email_header.name = name
                        email_header.value = value
                        email_headers.append(email_header)
                    if len(email_headers):
                        # Save reference to uid
                        new_email_headers.update({message.uid: email_headers})

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

                    for i in range(0, len(new_header_obj_list), query_batch_size):
                        EmailHeader.objects.bulk_create(new_header_obj_list[i:i + query_batch_size])

        elif not new_messages:
            task_logger.info('Saving these messages with custom concatenated SQL since they need to be updated')

            # Build query string and parameter list
            total_query_string = ''
            param_list = []
            query_count = 0
            update_email_headers = {}

            # update_email_attachments = {}
            task_logger.info('Looping through %s messages', len(messages))
            for message in messages:
                query_string = 'UPDATE email_emailmessage SET '
                if message.get_flags() is not None:
                    query_string += 'flags = %s, '
                    param_list.append(str(message.get_flags()))

                body_html = message.get_html_body()
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
                    for name, value in headers.items():
                        email_header = EmailHeader()
                        email_header.name = name
                        email_header.value = value
                        email_headers.append(email_header)
                    if len(email_headers):
                        # Save reference to uid
                        update_email_headers.update({message.uid: email_headers})

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

                    EmailAttachment.objects.filter(attachment='messaging/email/attachments/%(tenant_id)d/%(account_id)d/%(folder_name)s/%(filename)s')

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

                if query_count == query_batch_size:
                    # Execute queries
                    task_logger.info('Executing query batch (%s) now - queries for e-mail messages (full batch)', query_count)
                    cursor = connection.cursor()
                    cursor.execute(total_query_string, param_list)
                    query_count = 0  # reset counter

            # Execute leftover queries
            if query_count and query_count < query_batch_size:
                task_logger.info('Executing query batch (%s) now - queries for e-mail messages (leftovers next batch)', query_count)
                cursor = connection.cursor()
                cursor.execute(total_query_string, param_list)

            # Fetch message ids
            email_messages = EmailMessage.objects.filter(account=account, uid__in=[message.uid for message in messages], folder_name=folder.name_on_server).values_list('id', 'uid')

            # Find existing headers per email message
            existing_headers_per_message = {}
            existing_headers_qs = EmailHeader.objects.filter(message_id__in=[id for id, uid in email_messages]).values_list('message_id', 'name')
            for message_id, header_name in existing_headers_qs:
                headers = existing_headers_per_message.get(message_id, [])
                headers.append(header_name)
                existing_headers_per_message.update({message_id: headers})

            # Link message ids to headers and (inline) attachments
            for id, uid in email_messages:
                header_obj_list = update_email_headers.get(uid)
                if header_obj_list:
                    for header_obj in header_obj_list:
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

                    if query_count == query_batch_size:
                        # Execute queries - queries for e-mail headers (full batch)
                        task_logger.info('Executing query batch (%s) now - queries for e-mail headers (full batch)', query_count)
                        cursor = connection.cursor()
                        cursor.execute(total_query_string, param_list)
                        query_count = 0  # reset counter

                # Execute leftover queries
                if query_count and query_count < query_batch_size:
                    task_logger.info('Executing query batch (%s) now - queries for e-mail headers (leftovers next batch)', query_count)
                    cursor = connection.cursor()
                    cursor.execute(total_query_string, param_list)
                else:
                    task_logger.info('Not executing queries yet')

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

    except Exception, e:
        print traceback.format_exc(e)

    task_logger.info('Messages saved')


def _task_prerun_listener(**kwargs):
    task_logger.warning('Task prerun listener')
    Random.atfork()


task_prerun.connect(_task_prerun_listener)
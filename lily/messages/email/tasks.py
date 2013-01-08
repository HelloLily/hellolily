import datetime
import traceback
from dateutil.tz import tzutc

import celery
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from imapclient import SEEN

from lily.messages.email.emailclient import LilyIMAP, ALLMAIL, DRAFTS, TRASH, SPAM, IMPORTANT
from lily.messages.email.models import EmailAccount, EmailMessage, EmailHeader, EmailAttachment
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser


def save_email_messages(messages, account, folder_name, new_messages=False):
    """
    Save messages in database for account. Folder_name needs to be the server name.
    """

    try:
        query_batch_size = 10000

        if new_messages:
            new_message_obj_list = []
            new_email_headers = {}
            # new_email_attachments = {}
            for uid, message in messages.items():
                # Create new object
                email_message = EmailMessage()
                if message.get('sent_date') is not None:
                    email_message.sent_date = message.get('sent_date')
                email_message.account = account

                email_message.uid = uid
                if message.get('flags') is not None:
                    email_message.is_seen = SEEN in message.get('flags')
                    email_message.flags = message.get('flags')
                body = message.get('html_body') or message.get('plain_body')
                if body is not None:
                    email_message.body = body
                email_message.size = message.get('size')
                email_message.folder_name = folder_name
                email_message.is_private = False
                email_message.tenant = account.tenant
                email_message.polymorphic_ctype = ContentType.objects.get_for_model(EmailMessage)
                # Add to object list
                new_message_obj_list.append(email_message)

                # Check for headers
                if message.get('headers') is not None:
                    headers = message.get('headers')

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
                        new_email_headers.update({uid: email_headers})

                # Check for attachments
                # TODO
                # email_attachments = []
                # for attachment in message.get('attachments', []) or []:
                #     email_attachment = EmailAttachment()
                #     email_attachment.filename = attachment.get('filename')
                #     email_attachment.message = email_message
                #     email_attachment.tenant = account.tenant
                #     # email_attachment.file = File(filename=attachment.get('filename'), content=attachment.get('payload'))
                #     email_attachment.size = attachment.get('size')
                #     email_attachments.append(email_attachment)
                # if len(email_attachments):
                #     # Save reference to uid
                #     new_email_attachments.update({uid: email_attachments})

            # Save new_email_messages
            if len(new_message_obj_list):
                for i in range(0, len(new_message_obj_list), query_batch_size):
                    EmailMessage.objects.bulk_create(new_message_obj_list[i:i + query_batch_size])

                # Fetch message ids
                email_messages = EmailMessage.objects.filter(account=account, uid__in=messages.keys(), folder_name=folder_name).values_list('id', 'uid')

                # Link message ids to headers and attachments
                for id, uid in email_messages:
                    header_obj_list = new_email_headers.get(uid)
                    if header_obj_list:
                        for header_obj in header_obj_list:
                            header_obj.message_id = id

                    # attachment_obj_list = new_email_attachments.get(uid)
                    # if attachment_obj_list:
                    #     for attachment_obj in attachment_obj_list:
                    #         attachment_obj.message_id = id

                # Save new_email_headers
                if len(new_email_headers):
                    new_header_obj_list = []
                    # Add header to object list
                    for uid, headers in new_email_headers.items():
                        for header in headers:
                            new_header_obj_list.append(header)

                    for i in range(0, len(new_header_obj_list), query_batch_size):
                        EmailHeader.objects.bulk_create(new_header_obj_list[i:i + query_batch_size])

            # Save new_email_attachments
            # TODO

        elif not new_messages:
            # Build query string and parameter list
            total_query_string = ''
            param_list = []
            query_count = 0
            update_email_headers = {}
            # update_email_attachments = {}
            for uid, message in messages.items():
                query_string = 'UPDATE email_emailmessage SET '
                if message.get('sent_date') is not None:
                    query_string += 'sent_date = %s, '
                    param_list.append(datetime.datetime.strftime(message.get('sent_date'), '%Y-%m-%d %H:%M'))
                if message.get('flags') is not None:
                    query_string += 'flags = %s, '
                    param_list.append(str(message.get('flags')))
                    query_string += 'is_seen = %s, '
                    param_list.append(SEEN in message.get('flags'))
                body = message.get('html_body') or message.get('plain_body')
                if body is not None:
                    query_string += 'body = %s, '
                    param_list.append(body)
                if query_string.endswith(', '):
                    query_string = query_string.rstrip(', ')
                    query_string += ' WHERE tenant_id = %s AND account_id = %s AND uid = %s AND folder_name = %s;\n'
                    param_list.append(account.tenant_id)
                    param_list.append(account.id)
                    param_list.append(uid)
                    param_list.append(folder_name)

                    total_query_string += query_string
                    query_count += 1

                # Check for headers
                if message.get('headers') is not None:
                    headers = message.get('headers')

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
                        update_email_headers.update({uid: email_headers})

                # Check for attachments
                # TOOD

                if query_count == query_batch_size:
                    # Execute queries
                    cursor = connection.cursor()
                    cursor.execute(total_query_string, param_list)
                    query_count = 0  # reset counter

            # Execute leftover queries
            if query_count and query_count < query_batch_size:
                cursor = connection.cursor()
                cursor.execute(total_query_string, param_list)

            # Fetch message ids
            email_messages = EmailMessage.objects.filter(account=account, uid__in=messages.keys(), folder_name=folder_name).values_list('id', 'uid')

            # Link message ids to headers and attachments
            for id, uid in email_messages:
                header_obj_list = update_email_headers.get(uid)
                if header_obj_list:
                    for header_obj in header_obj_list:
                        header_obj.message_id = id

                # attachment_obj_list = new_email_attachments.get(uid)
                # if attachment_obj_list:
                #     for attachment_obj in attachment_obj_list:
                #         attachment_obj.message_id = id

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
                for header_obj in update_header_obj_list:
                    query_string = 'UPDATE email_emailheader SET '
                    query_string += 'value = %s '

                    query_string += 'WHERE name = %s AND message_id = %s;\n'
                    param_list.append(header_obj.value)
                    param_list.append(header_obj.name)
                    param_list.append(header_obj.message_id)

                    total_query_string += query_string
                    query_count += 1

                    if query_count == query_batch_size:
                        # Execute queries
                        cursor = connection.cursor()
                        cursor.execute(total_query_string, param_list)
                        query_count = 0  # reset counter

                # Execute leftover queries
                if query_count and query_count < query_batch_size:
                    cursor = connection.cursor()
                    cursor.execute(total_query_string, param_list)

            # Save new_email_attachments
            # TODO

    except Exception, e:
        print traceback.format_exc(e)


def get_unread_emails(accounts, page=1):
    """
    Retrieve unread messages for accounts.
    """
    for account in accounts:
        last_sync_date = account.last_sync_date
        if not last_sync_date:
            last_sync_date = datetime.datetime.fromtimestamp(0)
        last_sync_date = last_sync_date.astimezone(tzutc())
        new_sync_date = datetime.datetime.now(tzutc())

        # Check for new messages
        delta = new_sync_date - last_sync_date
        if delta.total_seconds() > 0:
            server = None
            try:
                server = LilyIMAP(provider=account.provider, account=account)

                synchronize_folder(server, folder_name=server.get_server_name_for_folder(ALLMAIL), criteria=['UNSEEN'])
            except Exception, e:
                print traceback.format_exc(e)
            else:
                # Update last_sync_date
                account.last_sync_date = new_sync_date
                account.save()
            finally:
                if server:
                    server.logout()


def synchronize_folder(server, folder_name, criteria=['ALL'], modifiers_old=['FLAGS'], modifiers_new=['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE', 'INTERNALDATE']):
    """
    Fetch and store modifiers_old for UIDs already in the database and
    modifiers_new for UIDs that only exist remotely.
    """
    # Find already known uids
    known_uids_qs = EmailMessage.objects.filter(account=server.account, folder_name=server.get_server_name_for_folder(folder_name))
    if 'SEEN' in criteria:
        known_uids_qs = known_uids_qs.filter(is_seen=True)

    if 'UNSEEN' in criteria:
        known_uids_qs = known_uids_qs.filter(is_seen=False)

    known_uids = set(known_uids_qs.values_list('uid', flat=True))

    try:
        folder_count, remote_uids = server.search_in_folder(criteria=criteria, identifier=server.get_server_name_for_folder(folder_name), close=False)

        # Get the difference between local and server uids
        new_uids = list(set(remote_uids).difference(known_uids))

        # UIDs that no longer exist in this folder
        removed_uids = list(known_uids.difference(set(remote_uids)))

        # Delete removed_uids from known_uids
        [known_uids.discard(x) for x in removed_uids]
        known_uids = list(known_uids)

        # Delete from database
        EmailMessage.objects.filter(account=server.account, folder_name=server.get_server_name_for_folder(folder_name), uid__in=removed_uids).delete()

        if len(new_uids):
            # Retrieve modifiers_new for new_uids
            folder_messages = server.fetch_from_folder(identifier=folder_name, message_uids=new_uids, modifiers=modifiers_new, close=False)

            if len(folder_messages) > 0:
                save_email_messages(folder_messages, server.account, server.get_server_name_for_folder(folder_name), new_messages=True)

        if len(known_uids):
            # Renew modifiers_old for known_uids, TODO; check scenario where local_uids[x] has been moved/trashed
            folder_messages = server.fetch_from_folder(identifier=folder_name, message_uids=known_uids, modifiers=modifiers_old, close=False)

            if len(folder_messages) > 0:
                save_email_messages(folder_messages, server.account, server.get_server_name_for_folder(folder_name))

    except Exception, e:
        print traceback.format_exc(e)
    finally:
        server.close_folder()


@celery.task
@transaction.commit_manually
def synchronize_email_for_account(account_id):
    """
    Synchronize all e-mail for given account one-way (external to here).

    Headers normally do not change for existing e-mail messages.
    Therefore a selection will be made. Data which will be
    synchronized:
    - headers, flags, size for new messages, flags only for old ones
    - headers, body, flags, size for drafts folder

    TODO: load balance the workload for multiple workers. Per account or per page per account.
    """
    try:
        account = EmailAccount.objects.get(id=account_id)
    except Exception, e:
        print traceback.format_exc(e)
    else:
        now_utc_date = datetime.datetime.now(tzutc())

        # Check for account inactivity, by checking last login for all users of the account's tenant
        last_login_date = CustomUser.objects.filter(tenant=account.tenant).order_by('-last_login').values_list('last_login')[0][0]
        last_login_delta = now_utc_date - last_login_date
        if last_login_delta.total_seconds() > 14 * 86400:  # 14 days
            # Complete current open transaction
            transaction.commit()
            return

        # Retrieve all messages every 15 minutes
        last_sync_date = account.last_sync_date
        if not last_sync_date:
            last_sync_date = datetime.datetime.fromtimestamp(0)
        last_sync_date = last_sync_date.astimezone(tzutc())

        last_sync_delta = now_utc_date - last_sync_date
        if last_sync_delta.total_seconds() > 0:
            server = None
            try:
                # Built check for last_sync_date vs current datetime
                server = LilyIMAP(provider=account.provider, account=account)

                folders = server.get_folders(exclude=[ALLMAIL, DRAFTS, SPAM, TRASH, IMPORTANT])

                for folder in folders:
                    synchronize_folder(server, folder.get_server_name())

                modifiers_old = ['BODY.PEEK[]', 'FLAGS', 'RFC822.SIZE']
                modifiers_new = ['BODY.PEEK[HEADER.FIELDS (Reply-To Subject Content-Type To From Message-ID Sender In-Reply-To Received Date)]', 'FLAGS', 'RFC822.SIZE']
                synchronize_folder(server, server.get_server_name_for_folder(DRAFTS), modifiers_old=modifiers_old, modifiers_new=modifiers_new)

                account.last_sync_date = now_utc_date
                account.save()
            except Exception, e:
                transaction.rollback()
                print traceback.format_exc(e)
            else:
                transaction.commit()
            finally:
                if server:
                    server.logout()


# @celery.task.periodic_task(run_every=datetime.timedelta(seconds=60), expires=60)
# @celery.task.periodic_task(run_every=datetime.timedelta(seconds=60), options={"expires": 60.0})
@celery.task
def synchronize_email():
    """
    Synchronize e-mail messages for all e-mail accounts.
    """
    accounts = EmailAccount.objects.all()

    for account in accounts:
        synchronize_email_for_account(account.id)


@celery.task
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
            # Connect
            server = LilyIMAP(provider=account.provider, account=account)
            try:
                for folder_name, message_uids in folders.items():
                    if server.get_imap_server().folder_exists(folder_name):
                        server.get_imap_server().select_folder(folder_name)
                        if read:
                            # Mark as read
                            server.mark_as_read(message_uids)
                        else:
                            # Mark as unread
                            server.mark_as_unread(message_uids)

                        server.close_folder()
            finally:
                if server:
                    server.logout()

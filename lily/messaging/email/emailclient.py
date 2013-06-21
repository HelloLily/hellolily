import datetime
import email
import pytz
import StringIO  # can't always use cStringIO
import sys
import traceback

from bs4 import BeautifulSoup, Comment
from dateutil.parser import parse
from dateutil.tz import tzutc
from django.core.mail import get_connection
from django.utils.datastructures import SortedDict

from imapclient.imapclient import IMAPClient, SEEN, DRAFT
from lily.messaging.email.utils import flatten_html_to_text


sys.setrecursionlimit(5000)

INBOX = '\\Inbox'
SENT = '\\Sent'
DRAFTS = '\\Drafts'
TRASH = '\\Trash'
ALLMAIL = '\\AllMail'
SPAM = '\\Spam'
IMPORTANT = '\\Important'
STARRED = '\\Starred'

IMAP_XFOLDER_FLAGS = [INBOX, SENT, DRAFTS, TRASH, ALLMAIL, SPAM, IMPORTANT,
                      STARRED]


class Folder(object):
    def __init__(self, name_server, flags, name_locale=None, folder_identifier=None):
        self._name_server = name_server
        self.flags = flags
        self._name_locale = name_locale
        self.identifier = folder_identifier

    def get_server_name(self):
        '''
        Return the name of this identifier on the server.
        '''
        return self._name_server

    def has_locale_name(self):
        '''
        Check if this identifier has a locale name.
        '''
        return self._name_locale is not None

    def get_locale_name(self):
        '''
        Return the locale name for this identifier.
        '''
        return self._name_locale

    def get_name(self, full=False):
        '''
        Return the name for this identifier. Used locale name when available.
        If the identifier is a subfolder, only the last identifier name will be
        returned if 'full' is False.
        '''
        if self.has_locale_name():
            name = self.get_locale_name()
        else:
            name = self.get_server_name()

        if not full:
            # Only return last identifier name
            return name.split('/')[-1:][0]
        return name

    def is_subfolder(self):
        '''
        Checks whether or not this identifier is a sub identifier.
        '''
        return self._name_server.split('/')[-1:][0] != self._name_server

    def can_select(self):
        return not '\\Noselect' in self.flags

    def is_parent(self):
        return not '\\HasNoChildren' in self.flags

    def get_parent(self):
        '''
        Return the parent identifier when available.
        '''
        if not self.is_subfolder():
            return None
        return '/'.join(self._name_server.split('/')[:-1])

    def __str__(self):
        return self.get_name(full=True)

    def __unicode__(self):
        return u'%s' % self.__str__()

    def __repr__(self):
        return self.__unicode__()


class LilyIMAP(object):
    _servers = {}
    _conn_kwargs = {}
    folders = None

    def __init__(self, provider=None, account=None, use_uid=True, ssl=True, test=False, **kwargs):
        # Save these arguments for later use
        self._conn_kwargs.update(provider=provider, account=account, use_uid=use_uid, ssl=ssl, **kwargs)

        # Create folder mapping
        if not test:
            self.retrieve_and_map_folders()

    @property
    def account(self):
        return self._conn_kwargs.get('account')

    def _get_imap_client(self):
        provider = self._conn_kwargs.get('provider')
        account = self._conn_kwargs.get('account')
        use_uid = self._conn_kwargs.get('use_uid')
        ssl = self._conn_kwargs.get('ssl')

        server = False
        if provider is not None and account is not None:
            server = IMAPClient(provider.imap_host, provider.imap_port, use_uid, ssl)
        else:
            host = self._conn_kwargs.get('host')
            port = self._conn_kwargs.get('port')
            server = IMAPClient(host, port, use_uid, ssl)

        return server

    def _login_in_imap(self, imap_client):
        provider = self._conn_kwargs.get('provider')
        account = self._conn_kwargs.get('account')

        if provider is not None and account is not None:
            imap_client.login(account.username, account.password)
        else:
            username = self._conn_kwargs.get('username')
            password = self._conn_kwargs.get('password')
            imap_client.login(username, password)
        return imap_client

    def get_imap_server(self):
        server = self._servers.get('imap', False) or False
        if not server or server._imap.state in ['NONAUTH', 'LOGOUT']:
            imap_client = self._get_imap_client()
            if imap_client:
                server = self._login_in_imap(imap_client)
                self._servers['imap'] = server
        return server

    def get_smtp_server(self, fail_silently=False):
        """
        Return backend for sending emails.
        """
        provider = self._conn_kwargs.get('provider')
        account = self._conn_kwargs.get('account')
        use_tls = self._conn_kwargs.get('ssl')

        if provider is not None and account is not None:
            host = provider.smtp_host
            port = provider.smtp_port
            username = account.username
            password = account.password
        else:
            host = self._conn_kwargs.get('host')
            port = self._conn_kwargs.get('port')
            username = self._conn_kwargs.get('username')
            password = self._conn_kwargs.get('password')

        kwargs = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'use_tls': use_tls,
        }
        return get_connection('django.core.mail.backends.smtp.EmailBackend', fail_silently=fail_silently, **kwargs)

    def retrieve_and_map_folders(self):
        '''
        Retrieve identifier names and map known folders with possibly localized
        names to a set of default identifier names. Depends on the XLIST command.
        TODO: execute capabilities command and use a fallback if it has no XLIST.
        '''
        folders = []
        mapping = {}

        # Get identifier .list from server
        out = self.get_imap_server().xlist_folders()

        # If there are folderes, map them
        if not len(out) == 1 and out[0] is not None:
            for identifier in out:
                # Flags in [0], separator in [1], identifier name in [2]
                flags = identifier[0]
                name_server = None
                name_locale = identifier[2]
                folder_identifier = None

                # Test if a flag represents a default identifier name
                overlap = list(set(flags).intersection(set(IMAP_XFOLDER_FLAGS)))

                if len(overlap) == 1:
                    folder_identifier = overlap[0].lstrip('\\')
                    if '\\%s' % folder_identifier == INBOX:
                        # NOTE: special case, can only read from the server by
                        # using INBOX as identifier
                        name_server = folder_identifier
                    else:
                        name_server = name_locale
                else:
                    # There is no separate identifier name on the server
                    name_server = name_locale

                folder = Folder(name_server, flags, name_locale, folder_identifier)
                folders.append(folder)

                if folder_identifier is not None:
                    mapping[folder_identifier] = folder.get_server_name()

        # Store identifier list and mapping
        self.set_folders(folders)
        self.set_folder_mapping(mapping)

    def set_folder_mapping(self, mapping):
        '''
        Set a mapping for locale identifier names to identifier names in
        IMAP_XFOLDER_FLAGS.
        '''
        self.IMAP_FOLDERS_DICT = mapping

    def set_folders(self, folders):
        '''
        Set a list of folders as available for the current connected server.
        '''
        self.folders = folders

    def get_folders(self, exclude=[], all=False):
        '''
        Return a list of Folder objects representing all folders on the current
        connected server. If all is True, folders that cannot be selected will
        be returned also. Folders in exclude are not returned (i.e. Trash/Drafts).
        '''
        folders = []
        for folder in self.folders:
            # Test exclude
            include = True
            for identifier in exclude:
                if isinstance(identifier, Folder) and identifier.identifier == folder.identifier:
                    include = False
                elif identifier.lstrip('\\') == folder.identifier:
                    include = False
                else:
                    folder_obj = self.get_folder_by_identifier(identifier)
                    if folder_obj is None:
                        folder_obj = self.get_folder_by_name(identifier)
                    if folder_obj is not None:
                        if folder_obj.get_server_name() == folder.get_server_name():
                            include = False

            if include:
                if folder.can_select() or not folder.can_select() and all:
                    folders.append(folder)
        return folders

    def get_folder_by_identifier(self, identifier):
        '''
        Return the Folder for the current server for given identifier.
        '''
        result = None
        if identifier in IMAP_XFOLDER_FLAGS:
            for folder in self.get_folders(all=True):
                if '\\%s' % folder.identifier == identifier:
                    result = folder
                    break
        return result

    def get_folder_by_name(self, folder_name):
        '''
        Return the Folder for the current server for given folder name.
        '''
        result = None
        for folder in self.get_folders(all=True):
            if folder.get_server_name() == folder_name:
                result = folder
                break
        return result

    def get_folder(self, folder):
        """
        Return the Folder instance for given folder.
        Folder can be a Folder object, identifier or folder name.
        """
        folder_obj = None
        if isinstance(folder, Folder):
            folder_obj = folder
        else:
            folder_obj = self.get_folder_by_identifier(folder)
            if folder_obj is None:
                folder_obj = self.get_folder_by_name(folder)
            if folder_obj is not None:
                folder_obj = folder_obj
        return folder_obj

    def get_server_name(self, folder):
        """
        Return the Folder's server name for given folder.
        Folder can be a Folder object, identifier or folder name.
        """
        folder_obj = self.get_folder(folder)
        if folder_obj is not None:
            return folder_obj.get_server_name()
        return None

    def parse_attachment(self, message_part):
        """
        Parse an attachment from a message part. Returns a StringIO object or None.
        """
        content_disposition = message_part.get('Content-Disposition', None)
        if content_disposition:
            dispositions = content_disposition.strip().split(';')
            if bool(content_disposition and dispositions[0].lower() in ['attachment', 'inline'] and message_part.get_filename() is not None):
                # Make sure not to use cStringIO; cStringIO can't set these attributes
                file_data = message_part.get_payload(decode=True)
                if file_data is not None:
                    attachment = StringIO.StringIO(file_data)
                    attachment.content_type = message_part.get_content_type()
                    attachment.size = len(file_data)
                    attachment.name = message_part.get_filename()
                    return attachment

        return None

    def get_message_from_raw(self, raw_data):
        """
        Return a dictionary with all message information. raw_data contains the
        response from the imap server.
        # TODO, check server capabilities and add [X-GM-THRID, X-GM-MSGID, X-GM-LABELS] ?
        """
        headers = None
        is_plain = False
        flags = None
        from_email = None
        to_email = None
        subject = None
        size = None
        sent_date = None
        attachments = None
        has_attachments = False
        html_body = None
        plain_body = None

        # Find key for header
        header_key = [key for key in raw_data.keys() if key.startswith('BODY[HEADER')] or None
        if header_key is not None:
            header_key = header_key[0]

        if 'FLAGS' in raw_data:
            flags = raw_data.get('FLAGS', ())

        # Parse headers
        if 'BODY[]' in raw_data or header_key is not None:
            # Read payload
            data = raw_data.get('BODY[]', raw_data.get(header_key))
            message = email.message_from_string(data)

            # Properly read headers
            headers = dict(message.items())
            for name, value in headers.items():
                decoded_fragments = email.header.decode_header(value)
                header_fragments = []
                for fragment, encoding in decoded_fragments:
                    if encoding is not None:
                        fragment = unicode(fragment, encoding).encode('utf-8', 'replace')
                    header_fragments.append(fragment)
                headers[name] = ''.join(header_fragments)

            if 'Content-Type' in headers:
                headers['Content-Type'] = headers['Content-Type'].split(';')[0]
            is_plain = headers.get('Content-Type', '').startswith('text/plain')
            from_email = message.get('From')
            to_email = message.get('To')
            subject = message.get('Subject')
            size = raw_data.get('RFC822.SIZE', 0)

            if message.get('Received') is not None or message.get('Date') is not None:
                # Convert header to UTC
                if message.get('Received') is not None:
                    origin_time = message.get('Received').replace('\r\n', '').replace('\n', '').split(';')[-1].strip()
                else:
                    origin_time = message.get('Date').strip()

                try:
                    parsed_time = parse(origin_time)
                    if parsed_time.tzinfo:
                        parsed_time.tzinfo._name = None  # clear tzname to rely solely on the offset (not all tznames are supported)
                    sent_date = parsed_time.astimezone(tzutc())
                except Exception, e:
                    # No valid sent date could be parsed; fall back to INTERNALDATE.
                    # INTERNALDATE has no tzinfo, but force UTC anyway.
                    internal_date = raw_data.get('INTERNALDATE')
                    sent_date = pytz.utc.localize(internal_date)

            # Check for attachments
            if header_key is not None:
                has_attachments = headers.get('Content-Type', '').startswith('multipart/mixed')
            else:
                has_attachments = headers.get('Content-Type', '').startswith('multipart/mixed') and message.is_multipart()

        if 'BODY[]' in raw_data:
            html_body = plain_body = u''
            attachments = []

            # Read payload
            data = raw_data.get('BODY[]')
            message = email.message_from_string(data)
            for part in message.walk():
                # Check for attachment
                attachment = self.parse_attachment(part)
                if attachment:
                    attachments.append(attachment)
                    continue

                # Read body
                try:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue

                    # Use soup to parse html formatted e-mail messages
                    if part.get_content_type() == 'text/html':
                        soup = BeautifulSoup(payload)
                        try:
                            # First try, set charset
                            payload = payload.decode(part.get_content_charset())
                        except Exception, e:
                            try:
                                # Second try, use charset detection by beautifulsoup
                                payload = payload.decode(soup.original_encoding)
                            except Exception, e:
                                # Last resort, force utf-8, ignore errors
                                payload = payload.decode('utf-8', errors='ignore')
                    else:
                        try:
                            # First try, set charset
                            payload = payload.decode(part.get_content_charset())
                        except Exception, e:
                            # Last resort, force utf-8, ignore errors
                            payload = payload.decode('utf-8', errors='ignore')

                except Exception, e:
                    print traceback.format_exc(e)
                else:
                    try:
                        if part.get_content_type() == 'text/plain':
                            plain_body += payload
                        elif part.get_content_type() == 'text/html':
                            html_body += payload
                    except Exception, e:
                        print traceback.format_exc(e)

                if part.get_content_maintype() == 'multipart':
                    continue

                if part.get('Content-Disposition') is None:
                    continue

            # Create soup from body to alter html tags
            soup = BeautifulSoup(html_body)

            # Remove html comments
            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()

            # Make all anchors open outside the iframe
            for anchor in soup.findAll('a'):
                anchor.attrs.update({
                    'target': '_blank',
                })

            html_body = soup.renderContents()

        if plain_body:
            plain_body = flatten_html_to_text(plain_body)

        # Return useful data
        return {
            'flags': flags,
            'headers': headers,
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'size': size,
            'sent_date': sent_date,
            'is_plain': is_plain,
            'has_attachments': has_attachments,
            'html_body': html_body,
            'plain_body': plain_body,
            'attachments': attachments,
        }

    def get_modifiers_for_uid(self, uid, modifiers, folder=None):
        """
        Return modifiers for uid in a folder. Providing folder is
        recommended. As a uid only needs be unique per folder, it's possible
        that not the intended message is found and returned.
        """
        try:
            if not isinstance(uid, list):
                uid = [uid]

            # Fastest case
            if folder:
                folder_name = self.get_server_name(folder)
                if self.get_imap_server().folder_exists(folder_name):
                    self.get_imap_server().select_folder(folder_name)
                    response = self.get_imap_server().fetch(uid, modifiers)

                    if len(response.items()) > 0:
                        msgid, data = response.items()[0]
                        message = self.get_message_from_raw(data)
                        self.get_imap_server().close_folder()
                        message['folder_name'] = folder_name
                        return message
                    # Not found in given folder, return nothing
                    return {}

            # From here on, we're just guessing which message it is.
            # It's in no way reliable, since it just returns the first
            # message it finds with the uid.
            #
            # Look for common case: INBOX
            inbox = self.get_folder_by_identifier(INBOX)
            if inbox.get_server_name() == folder_name:
                self.get_imap_server().select_folder(folder_name)
                response = self.get_imap_server().fetch(uid, modifiers)

                if len(response.items()) > 0:
                    msgid, data = response.items()[0]
                    message = self.get_message_from_raw(data)
                    self.get_imap_server().close_folder()
                    message['folder_name'] = folder_name
                    return message

            # Look into other folders
            for folder in self.get_folders(exclude=[INBOX, ALLMAIL, folder_name]):
                folder_name = folder.get_server_name()
                if self.get_imap_server().folder_exists(folder_name):
                    # Open folder
                    self.get_imap_server().select_folder(folder_name)
                    response = self.get_imap_server().fetch(uid, modifiers)

                    if len(response.items()) > 0:
                        msgid, data = response.items()[0]
                        message = self.get_message_from_raw(data)
                        self.get_imap_server().close_folder()
                        message['folder_name'] = folder_name
                        return message
        except Exception, e:
            print traceback.format_exc(e)

        return {}

    def search_in_folder(self, identifier=None, criteria=['ALL'], readonly=True, paginate=False, page=1, page_size=10, close=True):
        """
        Return all message uids in given identifier filtered by
        criteria and the total count of messages in identifier.
        A single identifier can be either a string representing an
        identifier name or a 'Folder' object.
        """
        folder_name = self.get_server_name(identifier)
        if self.get_imap_server().folder_exists(folder_name):
            # Open folder
            select_info = self.get_imap_server().select_folder(folder_name, readonly)
            try:
                # Get total message count in folder
                folder_count = select_info['EXISTS']

                # Search messages in folder
                message_uids = self.get_imap_server().search(criteria)

                if paginate:
                    # Slice resultset
                    start = (page - 1) * page_size
                    end = start + page_size
                    message_uids = message_uids[start:end]

                return folder_count, message_uids
            except Exception, e:
                print traceback.format_exc(e)
            finally:
                if close:
                    # Close after reading
                    self.get_imap_server().close_folder()
        return 0, {}

    def fetch_from_folder(self, identifier=None, message_uids=None, modifiers=[], close=True):
        """
        Fetch messages by UIDs from an already selected folder.
        """
        try:
            messages = {}
            response = self.get_imap_server().fetch(message_uids, modifiers)

            for msgid, data in response.items():
                try:
                    messages[msgid] = self.get_message_from_raw(data)
                    messages[msgid]['folder_name'] = self.get_server_name(identifier)
                except Exception, e:
                    print traceback.format_exc(e)
        except Exception, e:
            print traceback.format_exc(e)
        finally:
            if close:
                # Close after reading
                self.get_imap_server().close_folder()
            return messages

    def delete_from_folder(self, identifier=None, message_uids=None, trash_only=True):
        """
        Delete messages by UIDs from from given identifier. Messages are moved
        to trash by default.
        """
        try:
            folder_name = self.get_server_name_for_folder(identifier)
            self.get_imap_server().select_folder(folder_name, readonly=False)
            if self.get_imap_server().folder_exists(folder_name):
                response = self.get_imap_server().delete_messages(message_uids)
                self.get_imap_server().close_folder()

                # TODO, remove from trash, seems to have no effect in Gmail - needs testing on a separate IMAP server
                # if not trash_only:
                #     uids_in_trash = []
                #     for msgid, data in response.items():
                #         uids_in_trash.append(msgid)

                #     folder_name = self.get_server_name_for_folder(TRASH)
                #     if self.get_imap_server().folder_exists(folder_name):
                #         self.get_imap_server().select_folder(folder_name, readonly=False)
                #         self.get_imap_server().delete_messages(uids_in_trash)

                #         self.get_imap_server().expunge()
                #         self.get_imap_server().close_folder()

        except Exception, e:
            print traceback.format_exc(e)

    def get_messages_in_folders(self, identifiers=[], criteria=['ALL'], modifiers=[], readonly=True, paginate=False, page=1, page_size=10):
        '''
        Return messsages in given identifiers filtered by criteria and
        the total count of messages in identifiers. A single
        identifier can be either a string representing an identifier
        name or a 'Folder' object.
        '''
        messages = SortedDict()
        for identifier in identifiers:
            # Opens folder, but don't close it yet
            folder_count, message_uids = self.search_in_folder(identifier=identifier, criteria=criteria, readonly=readonly, paginate=paginate, page=page, page_size=page_size, close=False)

            # Fetch modifiers from folder
            messages.update(self.fetch_from_folder(identifier=identifier, message_uids=message_uids, modifiers=modifiers))
        return page, page_size, folder_count, messages

    def get_folder_status(self, status, identifier=ALLMAIL):
        '''
        Return the status for given identifier. status can be one or more of
        ['MESSAGES', 'RECENT', 'UIDNEXT', 'UIDVALIDITY', 'UNSEEN'].
        '''
        folder_name = self.get_server_name_for_folder(identifier)
        return self.get_imap_server().folder_status(folder_name, status)

    def get_folder_unread(self, identifier=ALLMAIL):
        '''
        Return the count of unread messages in given identifier.
        '''
        return self.get_folder_status('UNSEEN', identifier)

    def mark_as_read(self, uids):
        '''
        Mark message as read. uids can be one or more.
        '''
        if isinstance(uids, list):
            uids = ','.join([str(val) for val in uids])
        else:
            uids = [uids]

        self.get_imap_server().add_flags(uids, [SEEN])

    def mark_as_unread(self, uids):
        '''
        Mark message as unread. uids can be one or more.
        '''
        if isinstance(uids, list):
            uids = ','.join([str(val) for val in uids])
        else:
            uids = [uids]

        self.get_imap_server().remove_flags(uids, [SEEN])

    def logout(self):
        try:
            self.get_imap_server().logout()
            del self._servers['imap']
        except Exception, e:
            print traceback.format_exc(e)

    def close_folder(self):
        try:
            self.get_imap_server().close_folder()
        except Exception, e:
            print traceback.format_exc(e)

    def save_draft(self, message):
        """
        Create a draft. Returns the UID for e-mail message in the DRAFTS folder.
        """
        if isinstance(message, basestring):
            message = unicode(email.message_from_string(message))

        folder_name = self.get_server_name_for_folder(DRAFTS)
        self.get_imap_server().select_folder(folder_name)
        response = self.get_imap_server().append(folder_name, message, flags=[DRAFT], msg_time=datetime.datetime.now(tzutc()))
        self.get_imap_server().close_folder()
        command, seq, uid, status = [part.strip('[]()') for part in response.split(' ')]

        return uid

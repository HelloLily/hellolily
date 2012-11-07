import collections
import email
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from imapclient.imapclient import IMAPClient, SEEN


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
        if not self.issubfolder():
            return None
        return self._name_server.split('/')[:-1][0].join('/')

    def __str__(self):
        return self.get_name(full=True)

    def __unicode__(self):
        return u'%s' % self.__str__()

    def __repr__(self):
        return self.__unicode__()


class LilyIMAP(object):
    folders = None
    server = None

    def __init__(self, username, password, host, port=None, use_uid=True, ssl=True):
        self._server = IMAPClient(host, port, use_uid, ssl)
        self._server.login(username, password)
        self.retrieve_and_map_folders()

    def retrieve_and_map_folders(self):
        '''
        Retrieve identifier names and map known folders with possibly localized
        names to a set of default identifier names. Depends on the XLIST command.
        TODO: execute capabilities command and use a fallback if it has no XLIST.
        '''
        folders = []
        mapping = {}

        # Get identifier .list from server
        out = self._server.xlist_folders()

        # If there are folderes, map them
        if not len(out) == 1 and out[0] is not None:
            for identifier in out:
                # Flags in [0], separator in [1], identifier name in [2]
                flags = identifier[0]
                name_server = None
                name_locale = identifier[2]
                folder_identifier = None
                # Test if a flag represents a default identifier name

                overlap = list((
                                collections.Counter(flags) &
                                collections.Counter(IMAP_XFOLDER_FLAGS)
                          ).elements())

                if len(overlap) == 1:
                    folder_identifier = overlap[0].lstrip('\\')
                    if '\\%s' % folder_identifier == INBOX:
                        # XXX: special case, can only read from the server by
                        #      using INBOX as identifier
                        name_server = folder_identifier
                    else:
                        name_server = name_locale
                else:
                    # There is no separate identifier name on the server
                    name_server = name_locale

                folders.append(Folder(name_server, flags, name_locale, folder_identifier))

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

    def get_folders(self, all=False):
        '''
        Return a list of Folder objects representing all folders on the current
        connected server. If all is True, folders that cannot be selected will
        be returned also.
        '''
        folders = []
        for identifier in self.folders:
            if identifier.can_select() or not identifier.can_select() and all:
                folders.append(identifier)
        return folders

    def get_server_name_for_folder(self, identifier):
        '''
        Return the name on the server for given identifier. Identifier can be either a
        string representing a identifier name or a 'Folder' object.
        '''
        if isinstance(identifier, Folder):
            return identifier.get_server_name()
        else:
            folder_name = None
            if identifier in IMAP_XFOLDER_FLAGS:
                for folder in self.get_folders(all=True):
                    if '\\%s' % folder.identifier == identifier:
                        folder_name = folder.get_server_name()

            folder_name = folder_name if folder_name else identifier
            return self.IMAP_FOLDERS_DICT.get(folder_name, folder_name)

    def get_message_from_raw(self, raw_data):
        '''
        Return a dictionary with all message information. raw_data contains the
        response from the imap server.
        # TODO, check server capabilities and add [X-GM-THRID, X-GM-MSGID, X-GM-LABELS]
        '''
        # Check if only headers were retrieved
        headers_only = raw_data.has_key('BODY[HEADER]')

        message = email.message_from_string(raw_data.get('BODY[]', raw_data.get('BODY[HEADER]')))
        headers = dict(message.items())
        body = ''

        # Check for text/plain
        is_plain = headers.get('Content-Type', '').startswith('text/plain')

        # Check for attachments
        if headers_only:
            has_attachments = headers.get('Content-Type', '').startswith('multipart/mixed')
        else:
            has_attachments = headers.get('Content-Type', '').startswith('multipart/mixed') and message.is_multipart()

        attachments = []
        if not headers_only:
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue

                if part.get('Content-Disposition') is None:
                    continue

                if part.get_filename():
                    payload = StringIO.StringIO()
                    payload.write(part.get_payload(decode=True))
                    payload.close()
                    attachments.append({
                        'filename': part.get_filename(),
                        'payload': payload,
                    })

        # Return useful data
        return {
            'flags': raw_data.get('Flags', ()),
            'headers': headers,
            'body': body,
            'is_plain': is_plain,
            'has_attachments': has_attachments,
            'attachments': attachments,
            'from': email.utils.parseaddr(message.get('From')),
            'to': email.utils.parseaddr(message.get('To')),
            'subject': message.get('Subject'),
            'size': raw_data.get('RFC822.SIZE', 0),  # in bytes
        }

    def messages_in_folder(self, identifier, readonly=False):
        '''
        Return all messsages in given identifier. Folder can be either a string
        representing a identifier name or a 'Folder' object.
        '''
        folder_name = self.get_server_name_for_folder(identifier)
        messages = {}
        if self._server.folder_exists(folder_name):
            # Read non-deleted messages in folder
            self._server.select_folder(folder_name, readonly)
            message_uids = self._server.search(['NOT DELETED'])
            response = self._server.fetch(message_uids, ['BODY.PEEK[HEADER]', 'FLAGS', 'RFC822.SIZE'])

            for msgid, data in response.items():
                messages[msgid] = self.get_message_from_raw(data)

            # Close after reading
            self._server.close_folder()
        return messages

    def get_folder_status(self, status, identifier=ALLMAIL):
        '''
        Return the status for given identifier. status can be one or more of
        ['MESSAGES', 'RECENT', 'UIDNEXT', 'UIDVALIDITY', 'UNSEEN'].
        '''
        folder_name = self.get_server_name_for_folder(identifier)
        return self._server.folder_status(folder_name, status)

    def get_folder_unread(self, identifier=ALLMAIL):
        '''
        Return the count of unread messages in given identifier.
        '''
        return self.get_folder_status('UNSEEN', identifier)

    # def send_email(self, sender, recipients, subject, template, **kwargs):
    #     '''
    #     Send a templated e-mail using kwargs to decide the contents. If 'body'
    #     is in kwargs, this will be used in the template's stead.
    #     '''
    #     use_template = not 'body' in kwargs.keys()
    #     # TODO

    def mark_as_read(self, msgids):
        '''
        Mark message as read. msgids can be one or more uids
        '''
        if isinstance(msgids, list):
            msgids = ','.join([str(val) for val in msgids])

        self._server.add_flags(msgids, [SEEN])

    def mark_as_unread(self, msgids):
        '''
        Mark message as unread. msgids can be one or more uids.
        '''
        if isinstance(msgids, list):
            msgids = ','.join([str(val) for val in msgids])
        self._server.remove_flags(msgids, [SEEN])

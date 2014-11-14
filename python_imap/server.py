from socket import error, gaierror
from imapclient.imapclient import IMAPClient, DELETED, SEEN
from imaplib import IMAP4

from python_imap.decorators import logout_on_failure
from python_imap.errors import is_login_error, IMAPConnectionError
from python_imap.folder import Folder, XLIST_FOLDER_FLAGS
from python_imap.logger import logger
from python_imap.message import Message


class IMAP(object):
    client = None
    _folders = None
    _folders_reverse = None
    _login_failed_reason = None

    auth_ok = True  # assume True until LoginError

    def __init__(self, host, port=None, ssl=True, use_uid=True, stream=False, silent_fail=False):  # pylint: disable=R0913
        """
        Initialisation and setup connection to IMAPClient.

        Arguments:
            host (str): address of host
            port (int): port to connect to
            ssl (boolean): True if ssl should be used
            use_uid (boolean): If True unique message UIDs be used for all calls
                that accept message ids (defaults to True).
            stream (boolean):  If True then *host* is used as the command to run
                to establish a connection to the IMAP server (defaults to False).
                This is useful for exotic connection or authentication setups.

        Raises:
            IMAPConnectionError: raised when connection cannot be established.
        """
        try:
            self.client = IMAPClient(host, port, use_uid, ssl, stream)
            self.client.normalise_times = False
        except (error, gaierror) as e:
            # Could not connect to IMAPClient.
            self.client = None
            logger.warn(e)
            if not silent_fail:
                raise IMAPConnectionError(str(e))

    def login(self, username, password):
        """
        IMAP login.

        Returns:
            Boolean: True if login is successful.
        """
        if self.client:
            try:
                if self.client._imap.state in ('NONAUTH', 'LOGOUT'):
                    self.client.login(username, password)
            except IMAP4.error, e:
                logger.warn(e)
                if is_login_error(e):
                    self.auth_ok = False
                return False
            else:
                return True
        # There is no connection to an IMAPClient, so login is not possible.
        return False

    def logout(self):
        """
        IMAP log out.
        """
        if self.client:
            if self.client._imap.state in ('SELECTED', 'AUTH'):
                self.client.logout()

    @logout_on_failure
    def _retrieve_folders(self):
        """
        Retrieve a list of the folders which exist on the IMAP server using
        XLIST.
        """
        xlist_folders = self.client.xlist_folders()

        self._folders = []
        self._folders_reverse = {}
        if not len(xlist_folders) == 1 and xlist_folders[0] is not None:
            is_child = False
            parents = []
            for (flags, separator, name_locale) in xlist_folders:  # pylint: disable=W0612
                common = set(flags).intersection(set(XLIST_FOLDER_FLAGS))
                name_on_server = name_locale
                try:
                    identifier = common.pop()
                except KeyError:
                    identifier = None

                folder = Folder(flags, name_on_server, name_locale, identifier)

                if u'\\HasChildren' in flags or u'\\HasNoChildren' not in flags:
                    parents.append(folder)

                if is_child:
                    is_parents_child = folder._set_as_child_of(parents[-1])
                    if not is_parents_child:
                        del parents[-1]
                is_child = len(parents) > 0

                self._folders.append(folder)
                if identifier is not None:
                    self._folders_reverse[identifier] = folder

    def get_folder_by_identifier(self, identifier):
        """
        Find a folder by `identifier`.

        Will retrieve the folders on the server if this wasn't done yet.

        Returns a `Folder` instance or None if not found.
        """
        if self._folders_reverse is None:
            self._retrieve_folders()

        folder = self._folders_reverse.get(identifier, None)

        return folder

    def get_folder_by_name(self, name):
        """
        Find a folder by `name`.

        Will retrieve the folders on the server if this wasn't done yet.

        Returns a `Folder` instance or None if not found.
        """
        if self._folders is None:
            self._retrieve_folders()

        for folder in self._folders:
            if folder.get_name(full=True) == name:
                return folder

        return None

    def get_folder(self, name_or_identifier):
        """
        Helper function to find a specific, trying for identifier and
        folder name.

        Returns a `Folder` instance or None if not found.
        """
        folder = self.get_folder_by_identifier(name_or_identifier)
        if folder is None:
            folder = self.get_folder_by_name(name_or_identifier)

        return folder

    def get_folders(self, exclude=None, cant_select=False, update=False):
        """
        Get a list of folders which match the arguments `exclude` and
        `cant_select`.

        Returns a list of `Folder` instances.

        Keyword Arguments:
            update (boolean): When True, (re-)fetch the folders from the
                server.
        """
        exclude = exclude or []

        if self._folders is None or update:
            self._retrieve_folders()

        exclude_names_on_server = []
        for folder in exclude:
            exclude_names_on_server.append(self.get_folder(folder).name_on_server)

        folders = []
        for folder in self._folders:
            if folder.name_on_server in exclude_names_on_server:
                continue

            if '\\Noselect' in folder.flags and cant_select:
                folders.append(folder)
            elif not '\\Noselect' in folder.flags:
                folders.append(folder)
        return folders

    @logout_on_failure
    def select_folder(self, name_on_server, readonly=True):
        """
        Select the IMAP folder named `name_on_server`.

        Returns a boolean to indicate whether or not the client is in SELECTED
        mode and a dict with folder data.
        """
        select_info = None
        if self.client.folder_exists(name_on_server):
            select_info = self.client.select_folder(name_on_server, readonly)

        return self.client._imap.state == 'SELECTED', select_info

    @logout_on_failure
    def get_messages(self, uids, modifiers, folder, readonly=True):  # pylint: disable=R0913
        """
        Retrieve `modifiers` data for messages identified by `uids` in `folder`.

        Returns the data as a list.
        """
        if not isinstance(uids, list):
            uids = [uids]

        if 'INTERNALDATE' not in modifiers:
            modifiers.append('INTERNALDATE')

        messages = []

        name = folder.get_search_name()
        is_selected, select_info = self.select_folder(name, readonly=readonly)  # pylint: disable=W0612
        if is_selected:
            logger.debug('Fetching %d messages from %s', len(uids), folder.get_name(full=True))

            response = self.client.fetch(uids, modifiers)

            if len(response.items()) > 0:
                for uid, data in response.items():
                    message = Message(data, uid=uid, folder=folder)
                    messages.append(message)

            self.client.close_folder()

        return messages

    def get_message(self, uid, modifiers, folder, readonly=True):  # pylint: disable=R0913
        """
        Retrieve `modifiers` data for message identified by `uid` in `folder`.

        Returns the data or None if not found.
        """
        messages = self.get_messages(uid, modifiers, folder, readonly=readonly)
        if len(messages) > 0:
            return messages[0]

        return None

    @logout_on_failure
    def get_uids(self, folder, criteria=None, paginate=False, page=1, page_size=10):  # pylint: disable=R0913
        """
        Retrieve message UIDs for `criteria` in `folder`.

        Returns the full message count and a list of (paginated) UIDs.
        """
        criteria = criteria or ['ALL']

        messages_in_folder_count = 0
        uids = []

        name = folder.get_search_name()
        is_selected, select_info = self.select_folder(name, readonly=True)
        if is_selected:
            messages_in_folder_count = select_info['EXISTS']

            uids = self.client.search(criteria)

            if paginate:
                start = (page - 1) * page_size
                end = start + page_size
                uids = uids[start:end]

        if is_selected:
            self.client.close_folder()

        return messages_in_folder_count, uids

    @logout_on_failure
    def append(self, folder, message, flags=(), msg_time=None):
        """
        Append `message` to `folder`.

        Returns UID for this message.
        """
        response = self.client.append(
            folder.get_search_name(),
            message,
            flags,
            msg_time=msg_time
        )

        # Extract uid from response
        server_response = [part.strip('[]()') for part in response.split(' ')]
        return int(server_response[2])

    @logout_on_failure
    def delete_messages(self, folder, uids):
        """
        Delete messages from the currently selected
        folder.

        Returns the flags set for each modified message.
        """
        response = None

        is_selected, select_info = self.select_folder(  # pylint: disable=W0612
            folder.get_search_name(),
            readonly=False
        )
        if is_selected:
            logger.debug('Deleting %d messages from %s', len(uids), folder.get_name(full=True))

            response = self.client.add_flags(uids, DELETED)
            self.client.close_folder()
        return response

    @logout_on_failure
    def toggle_seen(self, folder, uids, seen=True):
        """
        Toggle the flag `SEEN` for `uids` in `folder`.
        """
        response = None

        is_selected, select_info = self.select_folder(  # pylint: disable=W0612
            folder.get_search_name(),
            readonly=False
        )
        if is_selected:
            logger.debug('Marking %d messages from %s with seen=%s',
                        len(uids),
                        folder.get_name(full=True),
                        seen)
            if seen:
                response = self.client.add_flags(uids, [SEEN])
            else:
                response = self.client.remove_flags(uids, [SEEN])
            self.client.close_folder()

        return response

    @logout_on_failure
    def move_messages(self, uids, from_folder, to_folder_name):
        """
        Move messages to a specific folder. Creates the target folder
        if it doesn't exist.

        Returns whether or not a folder named `to_folder_name` was created.
        """
        created_target_folder = False

        # Get or create folder `to_folder_name`
        target_folder = self.get_folder(to_folder_name)
        if target_folder is None:
            self.client.create_folder(to_folder_name)
            created_target_folder = True

            # Clear cache so get_folder fetches the new created folder
            self._folders_reverse = None
            self._folders = None
            target_folder = self.get_folder(to_folder_name)
            logger.debug('Created target folder: %s', target_folder.get_name(full=True))

        is_selected, select_info = self.select_folder(from_folder.get_search_name(), readonly=False)  # pylint: disable=W0612
        if is_selected:
            self.client.copy(uids, target_folder.get_search_name())

            # Delete remote messages
            uids = ','.join([str(val) for val in uids])
            self.client.add_flags(uids, DELETED)
            self.client.close_folder()

        return created_target_folder

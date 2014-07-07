from socket import error, gaierror
from imapclient.imapclient import IMAPClient
from imaplib import IMAP4

from python_imap.folder import Folder, XLIST_FOLDER_FLAGS
from python_imap.logger import logger
from python_imap.message import Message


CATCH_LOGIN_ERRORS = [
    '[ALERT] Invalid credentials',
    '[ALERT] Please log in via your web browser',
    '[AUTHENTICATIONFAILED]',
    'Invalid credentials'
]


class IMAP(object):
    client = None
    _folders = None
    _folders_reverse = None
    _login_failed_reason = None

    def __init__(self, host, port=None, ssl=True, use_uid=True, stream=False):
        self.auth_ok = True
        try:
            self.client = IMAPClient(host, port, use_uid, ssl, stream)
            self.client.normalise_times = False
        except (error, gaierror) as e:
            self.client = None
            logger.warn(e.strerror)


    def login(self, username, password):
        if self.client:
            try:
                if self.client._imap.state in ('NONAUTH', 'LOGOUT'):
                    self.client.login(username, password)
            except IMAP4.error, e:
                for error in CATCH_LOGIN_ERRORS:
                    if e.message.startswith(error):
                        self.auth_ok = False
                logger.warn(e)
            else:
                if self.client._imap.state in ('SELECTED', 'AUTH'):
                    logger.debug('imap login success')
                    return True

        logger.debug('imap login fail')
        return False

    def logout(self):
        if self.client:
            if self.client._imap.state in ('SELECTED', 'AUTH'):
                try:
                    self.client.logout()
                except:
                    pass

            if self.client._imap.state in ('NONAUTH', 'LOGOUT'):
                logger.debug('imap logout success')
                return True

        logger.debug('imap logout fail')
        return False

    def _retrieve_folders(self):
        xlist_folders = self.client.xlist_folders()

        self._folders = []
        self._folders_reverse = {}
        if not len(xlist_folders) == 1 and xlist_folders[0] is not None:
            is_child = False
            parents = []
            for (flags, separator, name_locale) in xlist_folders:
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
        if self._folders_reverse is None:
            self._retrieve_folders()

        folder = self._folders_reverse.get(identifier, None)
        #if folder is None:
        #    folder = self._folders_reverse.get('\\%s' % identifier, None)

        return folder

    def get_folder_by_name(self, name):
        if self._folders is None:
            self._retrieve_folders()

        for folder in self._folders:
            if folder.get_name(full=True) == name:
                return folder

        return None

    def get_folder(self, search):
        folder = self.get_folder_by_identifier(search)
        if folder is None:
            folder = self.get_folder_by_name(search)

        return folder

    def get_folders(self, exclude=[], cant_select=False, update=False):
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

    def select_folder(self, name_on_server, readonly=True):
        select_info = None
        if self.client.folder_exists(name_on_server):
            select_info = self.client.select_folder(name_on_server, readonly)

        return self.client._imap.state == 'SELECTED', select_info

    def get_messages(self, uids, modifiers, folder, readonly=True, always_internaldate=True):
        if not isinstance(uids, list):
            uids = [uids]

        if always_internaldate and 'INTERNALDATE' not in modifiers:
            modifiers.append('INTERNALDATE')

        messages = []

        name = folder.get_search_name()
        is_selected, select_info = self.select_folder(name, readonly=readonly)
        if is_selected:
            logger.info('Fetching %d messages from %s' % (len(uids), folder.get_name(full=True)))

            response = self.client.fetch(uids, modifiers)

            if len(response.items()) > 0:
                for uid, data in response.items():
                    message = Message(data, uid=uid, folder=folder)
                    messages.append(message)

            self.client.close_folder()

        return messages

    def get_message(self, uid, modifiers, folder, readonly=True, always_internaldate=True):
        messages = self.get_messages(uid, modifiers, folder, readonly=readonly, always_internaldate=always_internaldate)
        if len(messages) > 0:
            return messages[0]

        return None

    def get_uids(self, folder, criteria=['ALL'], paginate=False, page=1, page_size=10):
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

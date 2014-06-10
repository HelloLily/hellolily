# Folder flags used to identify folders retrieved with the *XLIST* command
ALLMAIL = '\\AllMail'
DRAFTS = '\\Drafts'
IMPORTANT = '\\Important'
INBOX = '\\Inbox'
SENT = '\\Sent'
SPAM = '\\Spam'
STARRED = '\\Starred'
TRASH = '\\Trash'

XLIST_FOLDER_FLAGS = [
    ALLMAIL,
    DRAFTS,
    IMPORTANT,
    INBOX,
    SENT,
    SPAM,
    STARRED,
    TRASH
]


class Folder(object):
    flags = {}
    identifier = None
    name_on_server = None
    name_locale = None
    parent = None

    def __init__(self, flags, name_on_server, name_locale, identifier):
        self.flags = flags
        self.name_on_server = name_on_server
        self.name_locale = name_locale
        self.identifier = identifier

    def _set_as_child_of(self, parent):
        self.parent = None

        try:
            if self.name_on_server.index(parent.name_on_server) == 0:
                self.parent = parent
        except ValueError:
            pass

        return self.parent is not None

    def get_search_name(self):
        """
        Return IMAP name on server, usually *_name_on_server*.
        For INBOX, use identifier as name.
        """
        if self.identifier == INBOX:
            name = self.identifier.lstrip('\\')
        else:
            name = self.name_on_server

        return name

    def get_name(self, full=False):
        if self.name_locale is not None:
            name = self.name_locale
        else:
            name = self.name_on_server

        if not full:
            return name.split('/')[-1:][0]
        return name

    def __str__(self):
        return self.get_name(full=True)

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return self.__unicode__()

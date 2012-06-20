import re, datetime, imaplib, email


class Connector(object):
    """
    Class that is used to connect to email services and retrieve/send messages.

    """

    def __init__(self, host, port, user, password, connect=True):
        """
        Initialize the connector.

        Args:
            Host (str)      : a string representing the host to which a connection will be made
            Port (int)      : an integer representing the port on which we want to connect with the host
            User (str)      : the username with which to connect to the server
            Password (str)  : the password to use when connecting to the server
            Connect (bool)  : decides whether or not to automatically connect on initialisation

        Returns:
            An instance of the connector

        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.gmail = True if host == 'imap.gmail.com' else False

        if connect:
            self.connect()


    def connect(self):
        """
        Connect to the specified host via the specified port.

        Raises:
            GaiError: if host is a string but it is invalid, meaning no connection can be established
            Error: if port is an int but it is invalid, meaning no connection can be established

        """
        if not self.connection:
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)


    def is_valid_connection(self, host, port):
        """
        Test wether the host and port are valid, meaning we can get a connection to the provider.

        Args:
            Host (str)  : a string representing the host to which a connection will be tested
            Port (int)  : an integer representing the port on which we want to test the connection with the host

        Returns:
            True or False depending on the validity of the connection

        """
        try:
            self.connection = imaplib.IMAP4_SSL(str(host), int(port))
            return True
        except:
            return False


    def get_message_list(self, folder='INBOX', readonly=1, limit=None):
        """
        Returns a list of messages with an optional limit.

        Args:
            Limit (int) : optional argument to specify how much messages to return

        Returns:
            A list of messages

        """
        self.__login()
        self.connection.select(folder, readonly=readonly)

        result, data = self.connection.uid('search', None, "ALL") # search and return uids
        if result != 'OK':
            print 'result was: "', result, '", while the expected result was OK'

        if limit:
            uid_string =  ','.join(data[0].split()[-limit:])
        else:
            uid_string =  ','.join(data[0].split())

        message_list = self.__fetch_by_uid(uid_string)

        self.__logout()
        return message_list


    def import_messages(self):
        """
        Import a new mail account and save the messages to the database.

        """
        self.__login()
        self.connection.select('INBOX', readonly=1)

        result, data = self.connection.uid('search', None, "ALL") # search and return uids
        if result != 'OK':
            print 'result was: "', result, '", while the expected result was OK'

        uid_string =  ','.join(data[0].split())
        message_list = self.__fetch_by_uid(uid_string)

        for email in message_list:
            # save in database
            pass

        self.__logout()
        return

    def __login(self):
        """
        Perform a login if needed

        """
        if self.connection.state == 'NONAUTH':
            self.connection.login(self.user, self.password)


    def __logout(self):
        """
        Perform a logout if needed

        """
        if self.connection.state == 'AUTH':
            self.connection.logout()


    def __fetch_by_uid(self, uid_string):
        """
        Use the fetch command to get the messages in the uid_string.

        Args:
            uid_string (str)    : The string containing all uids of the messages that will be fetched

        """
        message_list = []

        if self.gmail:
            result, msg_data = self.connection.uid('fetch', uid_string, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID)')
        else:
            result, msg_data = self.connection.uid('fetch', uid_string, '(BODY.PEEK[] FLAGS)')

        if result != 'OK':
            print 'result was: "', result, '", while the expected result was OK'

        iterator = iter(msg_data)

        for it in iterator:
            email_message = {}
            messagePlainText = ''
            messageHTML = ''
            messageAttachments = []

            msg = email.message_from_string(it[1])
            for part in msg.walk():
                if str(part.get_content_type()) == 'text/plain':
                    messagePlainText += str(part.get_payload())
                if str(part.get_content_type()) == 'text/html':
                    messageHTML += str(part.get_payload(decode=True))
                if part.get_filename():
                    messageAttachments.append((part.get_filename(), part.get_payload(decode=True)))

            for key in msg.keys():
                email_message[key.lower().replace('-', '_')] = msg[key] if msg.has_key(key) else None

            d = email.Utils.parsedate(email_message['date'])
            from_str = email.Utils.parseaddr(email_message['from'])

            email_message.update({
                'from_name': from_str[0],
                'from_email': from_str[1],
                'message_text': messagePlainText,
                'message_html': messageHTML,
                'message_attachments': messageAttachments,
                'date': datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5]),
                'message_uid': re.search(r'(UID) ([\d]*)', it[0]).group(2),
                'message_flags': imaplib.ParseFlags(it[0]),
                'message_type': 'email',
            })

            if self.gmail:
                email_message.update({
                    'gmail_id': re.search(r'(X-GM-MSGID) ([\d]*)', it[0]).group(2),
                    'gmail_thread_id': re.search(r'(X-GM-THRID) ([\d]*)', it[0]).group(2),
                })

            iterator.next()

            message_list.append(email_message)

        return message_list
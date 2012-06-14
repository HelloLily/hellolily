import re, datetime, imaplib, email

date_format = "%d-%m-%Y %H:%M:%S"
con = imaplib.IMAP4_SSL('imap.gmail.com')


def get_message_list():
    __login(con)
    con.select('INBOX', readonly=1)
    
    result, data = con.uid('search', None, "ALL") # search and return uids instead
    if result != 'OK':
        print 'result was: "', result, '", while the expected result was OK'
    
    uid_string =  ','.join(data[0].split())
    message_list = __fetch_message_list(uid_string)
            
    __logout(con)
    return message_list


def __login(connection):
    if connection.state == 'NONAUTH':
        connection.login('lily@hellolily.com', '0$mxsq=3ouhr)_iz710dj!*2$vkz')


def __logout(connection):
    if connection.state == 'AUTH':
        connection.logout()


def __fetch_message_list(uid_string):
    message_list = []
        
    result, msg_data = con.uid('fetch', uid_string, '(BODY.PEEK[] FLAGS)')
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
                messagePlainText = messagePlainText + str(part.get_payload())
            if str(part.get_content_type()) == 'text/html':
                messageHTML = messageHTML + str(part.get_payload(decode=True))
            if part.get_filename():
                messageAttachments.append((part.get_filename(), part.get_payload(decode=True)))
        
        email_message['message_text'] = messagePlainText
        email_message['message_html'] = messageHTML
        email_message['message_attachements'] = messageAttachments
                    
        for key in msg.keys():
            email_message[key.lower().replace('-', '_')] = msg[key] if msg.has_key(key) else None
                    
        d = email.Utils.parsedate(email_message['date'])
        email_message['date'] = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
        
        email_message['from_name'], email_message['from_email'] = email.Utils.parseaddr(email_message['from'])
        email_message['message_uid'] = re.search(r'(UID) ([\d]*)', it[0]).group(2)
        email_message['message_flags'] = imaplib.ParseFlags(it[0])
        email_message['message_type'] = 'email'
        iterator.next()
        
        message_list.append(email_message)
    
    return message_list
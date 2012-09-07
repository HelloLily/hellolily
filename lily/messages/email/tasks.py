import re, datetime, imaplib, email

from celery.task import task
import sys

from lily.messages.email.models import EmailAttachment, EmailMessage


@task
def import_account(account):
    host = account.provider.retrieve_host
    port = account.provider.retrieve_port
    connection = imaplib.IMAP4_SSL(host, port)
    gmail = __is_gmail(account)

    connection.login(account.username, account.password)

    # get all messages for provided accounts
    connection.select('INBOX', readonly=1)

    result, data = connection.uid('search', None, "ALL") # search and return uids
    if result != 'OK':
        print 'result was: "', result, '", while the expected result was OK'

    uid_string =  ','.join(data[0].split())
    message_list = []

    if gmail:
        result, msg_data = connection.uid('fetch', uid_string, '(BODY.PEEK[] FLAGS X-GM-THRID X-GM-MSGID)')
    else:
        result, msg_data = connection.uid('fetch', uid_string, '(BODY.PEEK[] FLAGS)')

    if result != 'OK':
        print 'result was: "', result, '", while the expected result was OK'

    iterator = iter(msg_data)

    for it in iterator:
        email_message = EmailMessage()
        messageAttachments = []
        messagePlainText = ''
        messageHTML = ''

        msg = email.message_from_string(it[1])
        for part in msg.walk():
            if str(part.get_content_type()) == 'text/plain':
                messagePlainText += str(part.get_payload())
            if str(part.get_content_type()) == 'text/html':
                messageHTML += str(part.get_payload(decode=True))
            if part.get_filename():
                messageAttachments.append((part.get_filename(), part.get_payload(decode=True)))

        for key in msg.keys():
            if hasattr(email_message, key.lower().replace('-', '_')):
                setattr(email_message, key.lower().replace('-', '_'), msg[key])

        d = email.Utils.parsedate(msg['Date'])
        from_str = email.Utils.parseaddr(msg['From'])

        email_message.from_name = from_str[0]
        email_message.from_email = from_str[1]
        email_message.message_text = messagePlainText
        email_message.message_html = messageHTML

        # TODO: attachments should be saved in attachment model
        #email_message.message_attachments = messageAttachments

        email_message.datetime = datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
        email_message.message_uid = re.search(r'(UID) ([\d]*)', it[0]).group(2)
        email_message.message_flags = imaplib.ParseFlags(it[0])

        if gmail:
            email_message.gmail_id = re.search(r'(X-GM-MSGID) ([\d]*)', it[0]).group(2)
            email_message.gmail_thread_id = re.search(r'(X-GM-THRID) ([\d]*)', it[0]).group(2)

#        email_message.update({
#            'from_name': from_str[0],
#            'from_email': from_str[1],
#            'message_text': messagePlainText,
#            'message_html': messageHTML,
#            'message_attachments': messageAttachments,
#            'date': datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5]),
#            'message_uid': re.search(r'(UID) ([\d]*)', it[0]).group(2),
#            'message_flags': imaplib.ParseFlags(it[0]),
#            'message_type': 'email',
#            })
#
#        if gmail:
#            email_message.update({
#                'gmail_id': re.search(r'(X-GM-MSGID) ([\d]*)', it[0]).group(2),
#                'gmail_thread_id': re.search(r'(X-GM-THRID) ([\d]*)', it[0]).group(2),
#                })

        iterator.next()

        message_list.append(email_message)

    connection.logout()
    return message_list


@task
def update_account(account):
    host = account.provider.retrieve_host
    port = account.provider.retrieve_port
    connection = imaplib.IMAP4_SSL(host, port)

#    connection.login(account.username, account.password)

    # get new messages for provided accounts

#    connection.logout()

    return __is_gmail(account)


def __is_gmail(account):
    if account.provider.retrieve_host == 'imap.gmail.com':
        return True
    return False
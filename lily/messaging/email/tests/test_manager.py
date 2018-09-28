# -*- coding: utf-8 -*-
import json

import anyjson
from googleapiclient.discovery import build
from rest_framework.test import APITestCase

from lily.messaging.email.connector import GmailConnector
from lily.messaging.email.factories import EmailAccountFactory, EmailMessageFactory, EmailLabelFactory
from lily.messaging.email.manager import GmailManager
from lily.messaging.email.models.models import EmailAccount, EmailMessage, EmailLabel, EmailOutboxMessage
from lily.messaging.email.services import GmailService
from lily.settings import settings
from lily.tests.utils import UserBasedTest, get_dummy_credentials

from mock import patch


class GmailManagerTests(UserBasedTest, APITestCase):
    """
    Class for unit testing the GmailManager.
    """

    def setUp(self):
        # Patch the creation of a Gmail API service without the need for authorized credentials.
        credentials = get_dummy_credentials()
        self.get_credentials_mock_patcher = patch('lily.messaging.email.connector.get_credentials')
        get_credentials_mock = self.get_credentials_mock_patcher.start()
        get_credentials_mock.return_value = credentials

        self.authorize_mock_patcher = patch.object(GmailService, 'authorize')
        authorize_mock = self.authorize_mock_patcher.start()
        authorize_mock.return_value = None

        self.build_service_mock_patcher = patch.object(GmailService, 'build_service')
        build_service_mock = self.build_service_mock_patcher.start()
        build_service_mock.return_value = build('gmail', 'v1', credentials=credentials)

    @classmethod
    def setUpTestData(cls):
        # Create a user, handled by UserBasedTest.
        super(GmailManagerTests, cls).setUpTestData()

        # Create an email account for the user.
        EmailAccountFactory.create(owner=cls.user_obj, tenant=cls.user_obj.tenant)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    @patch.object(GmailConnector, 'get_all_message_id_list')
    @patch('lily.messaging.email.manager.app.send_task')
    def test_full_synchronize(self, send_task_mock, get_all_message_id_list_mock):
        """
        Test the GmailManager full synchronize. Verify that the message id's are processed correct by lookng at the
        correct number of calls on the http mock object.
        """
        send_task_mock.return_value = True

        with open('lily/messaging/email/tests/data/all_message_id_list_single_page.json') as infile:
            json_obj = json.load(infile)
            messages = json_obj['messages']
            get_all_message_id_list_mock.return_value = messages

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.full_synchronize()

        # Count the number of times the send_task mock was called to download a new message or to administer the
        # synchronization finished.
        call_download_email_message_count = sum(
            call[0][0] == 'download_email_message' for call in send_task_mock.call_args_list)
        call_full_sync_finished_count = sum(
            call[0][0] == 'full_sync_finished' for call in send_task_mock.call_args_list)

        self.assertEqual(call_download_email_message_count, len(messages))
        self.assertEqual(call_full_sync_finished_count, 1)

    @patch.object(GmailConnector, 'get_message_info')
    def test_download_message(self, get_message_info_mock):
        """
        Test the GmailManager on downloading a message and that it is stored in the database.
        """
        message_id = '15a6008a4baa65f3'

        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()

        labels = [settings.GMAIL_LABEL_UNREAD, settings.GMAIL_LABEL_INBOX]
        for label in labels:
            EmailLabelFactory.create(account=email_account, label_id=label)

        manager = GmailManager(email_account)
        # Message isn't present in the db, so it will do a mocked API call.
        manager.download_message(message_id)

        # Verify that the email message is stored in the db.
        self.assertTrue(EmailMessage.objects.filter(account=email_account, message_id=message_id).exists())

        # Verify that the email message has the correct labels.
        email_message = EmailMessage.objects.get(account=email_account, message_id=message_id)
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set([settings.GMAIL_LABEL_UNREAD, settings.GMAIL_LABEL_INBOX]))

    @patch.object(GmailConnector, 'get_short_message_info')
    @patch.object(GmailConnector, 'get_message_info')
    def test_download_message_exists(self, get_message_info_mock, get_short_message_info_mock):
        """
        Test the GmailManager on updating an existing message.
        """
        message_id = '15a6008a4baa65f3'

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)

        labels = [settings.GMAIL_LABEL_UNREAD, settings.GMAIL_LABEL_INBOX]
        for label in labels:
            EmailLabelFactory.create(account=email_account, label_id=label)

        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        # Message isn't present in the db, so it will do a mocked API call.
        manager.download_message(message_id)

        # The message with labels is now present in the database so downloading it again will only update it's labels.
        with open('lily/messaging/email/tests/data/get_short_message_info_{0}_archived.json'.format(
                message_id)) as infile:
            json_obj = json.load(infile)
            get_short_message_info_mock.return_value = json_obj

        try:
            manager.download_message(message_id)
        except StopIteration:
            # Because the email message is already in the database it should not do a (mocked) API call again.
            self.fail('StopIteration should have been raised.')

        # Verify that the email message has the correct labels after the updated short message info with the Inbox
        # label removed.
        email_message = EmailMessage.objects.get(account=email_account, message_id=message_id)
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set([settings.GMAIL_LABEL_UNREAD]))

    @patch.object(GmailConnector, 'get_label_list')
    def test_sync_labels(self, get_label_list_mock):
        """
        Test the GmailManager on synchronizing the labels for the email account.
        """
        mock_list = []
        # Mock adding new labels.
        with open('lily/messaging/email/tests/data/get_label_list.json') as infile:
            json_obj = json.load(infile)
            api_labels_count = len(json_obj['labels'])
            mock_list.append(json_obj['labels'])

        # Mock renaming two labels.
        with open('lily/messaging/email/tests/data/get_label_list_rename.json') as infile:
            json_obj = json.load(infile)
            mock_list.append(json_obj['labels'])

        # Mock removing two labels.
        with open('lily/messaging/email/tests/data/get_label_list_remove.json') as infile:
            json_obj = json.load(infile)
            mock_list.append(json_obj['labels'])

        get_label_list_mock.side_effect = mock_list

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.sync_labels()  # First mock will add new labels to the database.

        # Verify that the correct number of labels are present in the database.
        self.assertEqual(EmailLabel.objects.filter(account=email_account).count(), api_labels_count)

        # Verify the names of the two labels before the rename.
        label_1 = EmailLabel.objects.get(account=email_account, label_id='Label_1')
        label_2 = EmailLabel.objects.get(account=email_account, label_id='Label_2')
        self.assertEqual('label one', label_1.name, 'Label name before renaming is incorrect.')
        self.assertEqual('label two', label_2.name, 'Label name before renaming is incorrect.')

        manager.sync_labels()  # Second mock will rename two labels in the database.

        # Verify that the correct number of labels are still present in the database.
        self.assertEqual(EmailLabel.objects.filter(account=email_account).count(), api_labels_count)

        # Verify the names of the two labels after the rename.
        label_1.refresh_from_db()
        label_2.refresh_from_db()
        self.assertEqual('label one renamed', label_1.name, 'Label name after renaming is incorrect.')
        self.assertEqual('label two renamed', label_2.name, 'Label name after renaming is incorrect.')

        # Verify that the two specific labels are present before removing.
        self.assertTrue(EmailLabel.objects.filter(account=email_account, label_id='Label_1').exists())
        self.assertTrue(EmailLabel.objects.filter(account=email_account, label_id='Label_2').exists())

        manager.sync_labels()  # Third mock will remove two labels from the database.

        # Verify that the correct number of labels present in the database, which is 2 less then initially were added.
        self.assertEqual(EmailLabel.objects.filter(account=email_account).count(), api_labels_count - 2)

        # Verify that the two specific labels are removed.
        self.assertFalse(EmailLabel.objects.filter(account=email_account, label_id='Label_1').exists())
        self.assertFalse(EmailLabel.objects.filter(account=email_account, label_id='Label_2').exists())

    @patch.object(GmailConnector, 'get_label_info')
    def test_get_label(self, get_label_info_mock):
        """
        Test the GmailManager on getting the label info via an API call and that it is stored in the database.
        """
        with open('lily/messaging/email/tests/data/get_label_info_INBOX.json') as infile:
            json_obj = json.load(infile)
            get_label_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        # Label isn't present in the db, so it will do a mocked API call.
        label = manager.get_label(settings.GMAIL_LABEL_INBOX)

        # Verify that the Inbox label is present in the database.
        self.assertIsNotNone(label)
        self.assertTrue(EmailLabel.objects.filter(account=email_account, label_id=settings.GMAIL_LABEL_INBOX).exists())

    @patch.object(GmailConnector, 'get_label_info')
    def test_get_label_exists(self, get_label_info_mock):
        """
        Test the GmailManager on getting the label info from the database.
        """
        with open('lily/messaging/email/tests/data/get_label_info_INBOX.json') as infile:
            json_obj = json.load(infile)
            get_label_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        # Label isn't present in the db, so it will do a mocked API call.
        label = manager.get_label(settings.GMAIL_LABEL_INBOX)

        # Verify that the Inbox label is present in the database.
        self.assertIsNotNone(label)
        self.assertTrue(EmailLabel.objects.filter(account=email_account, label_id=settings.GMAIL_LABEL_INBOX).exists())

        try:
            # Retrieve the same label again.
            manager.get_label(settings.GMAIL_LABEL_INBOX)
        except StopIteration:
            # Because the label is already in the database it should not do a (mocked) API call again.
            self.fail('StopIteration should have been raised.')

    def test_administer_sync_status_true(self):
        """
        Test the GmailManager on setting the full sync status to in progress on the email account.
        """
        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.administer_sync_status(True)

        self.assertTrue(email_account.is_syncing)
        self.assertEqual(email_account.sync_failure_count, 0)

    def test_administer_sync_status_false(self):
        """
        Test the GmailManager on setting the full sync status to not in progress on the email account.
        """
        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.administer_sync_status(False)

        self.assertFalse(email_account.is_syncing)
        self.assertEqual(email_account.sync_failure_count, 0)

    @patch.object(GmailConnector, 'get_label_info')
    @patch.object(GmailConnector, 'send_email_message')
    @patch.object(GmailConnector, 'get_message_info')
    def test_send_email_message(self, get_message_info_mock, send_email_message_mock, get_label_info_mock):
        """
        Test the GmailManager on sending a new email message.
        """

        message_id = '15b33aad2c5dbe4a'

        # Mock the responses of the API calls.
        with open('lily/messaging/email/tests/data/send_email_message.json') as infile:
            json_obj = json.load(infile)
            send_email_message_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_label_info_SENT.json') as infile:
            json_obj = json.load(infile)
            get_label_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)

        # Prepare an email message that will be send out.
        email_outbox_message = EmailOutboxMessage.objects.create(
            subject="Mauris ex tortor, hendrerit non sem eu, mollis varius purus.",
            send_from=email_account,
            to=anyjson.dumps("user2@example.com"),
            cc=anyjson.dumps(None),
            bcc=anyjson.dumps(None),
            body="<html><body>In hac habitasse platea dictumst. Class aptent taciti sociosqu ad litora torquent "
                 "per conubia nostra, per inceptos himenaeos. Ut aliquet elit sed augue bibendum malesuada."
                 "</body></html>",
            headers={},
            mapped_attachments=0,
            template_attachment_ids='',
            original_message_id='',
            tenant=self.user_obj.tenant
        )

        # Send the email message.
        manager.send_email_message(email_outbox_message.message())

        # Verify that is stored in the database as an email message.
        self.assertTrue(EmailMessage.objects.filter(account=email_account, message_id=message_id).exists(),
                        "Send message missing from the database.")

        # Verify that the email message has the correct labels.
        email_message = EmailMessage.objects.get(account=email_account, message_id=message_id)
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set([settings.GMAIL_LABEL_SENT]), "Send message mssing the SEND label.")

        # Verify that the email emssage has the correct thread id. Because the email message is not part of a thread,
        # the thread_id should be the same as the message_id.
        self.assertEqual(email_message.thread_id, message_id, "Message_id and thread_id should be the same.")

    @patch.object(GmailConnector, 'get_label_info')
    @patch.object(GmailConnector, 'send_email_message')
    @patch.object(GmailConnector, 'get_message_info')
    def test_send_email_message_reply(self, get_message_info_mock, send_email_message_mock, get_label_info_mock):
        """
        Test the GmailManager on replying on an email message.
        """

        message_id = '15b3e2894fa3648d'
        thread_id = '15a6008a4baa65f3'

        # Mock the responses of the API calls.
        with open('lily/messaging/email/tests/data/send_email_message_reply.json') as infile:
            json_obj = json.load(infile)
            send_email_message_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_label_info_SENT.json') as infile:
            json_obj = json.load(infile)
            get_label_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)

        # Prepare an email message that will be send out.
        email_outbox_message = EmailOutboxMessage.objects.create(
            subject="Mauris ex tortor, hendrerit non sem eu, mollis varius purus.",
            send_from=email_account,
            to=anyjson.dumps("user2@example.com"),
            cc=anyjson.dumps(None),
            bcc=anyjson.dumps(None),
            body="<html><body>Maecenas metus turpis, eleifend at dignissim ac, feugiat vel erat. Aenean at urna "
                 "convallis, egestas massa sed, rhoncus est.<br><br>Firstname Lastname (user1@example.com) wrote on "
                 "22 March 2017 13:14:<hr><div dir=\"ltr\">Aliquam eleifend pharetra ligula, id feugiat ipsum laoreet "
                 "a. Aenean sed volutpat magna, ut viverra turpis. Morbi suscipit, urna in pellentesque venenatis, "
                 "mauris elit placerat justo, sit amet vestibulum purus dui id massa. In vitae libero et nunc "
                 "facilisis imperdiet. Sed pharetra aliquet luctus.</div></body></html>",
            headers={},
            mapped_attachments=0,
            template_attachment_ids='',
            original_message_id='',
            tenant=self.user_obj.tenant
        )

        # Send the email message, it will be a reply because a thead id is passed.
        manager.send_email_message(email_outbox_message.message(), thread_id=thread_id)

        # Verify that is stored in the database as an email message.
        self.assertTrue(EmailMessage.objects.filter(account=email_account, message_id=message_id).exists(),
                        "Send reply message missing from the database.")

        # Verify that the email message has the correct labels.
        email_message = EmailMessage.objects.get(account=email_account, message_id=message_id)
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set([settings.GMAIL_LABEL_SENT]), "Send message mssing the SEND label.")

        # Verify that the email emssage has the correct thread id.
        self.assertEqual(email_message.thread_id, thread_id,
                         "Message {0} should have thread_id {1}.".format(email_message.message_id, thread_id))

    @patch.object(GmailConnector, 'get_label_info')
    @patch.object(GmailConnector, 'send_email_message')
    @patch.object(GmailConnector, 'get_message_info')
    def test_send_email_message_unicode(self, get_message_info_mock, send_email_message_mock, get_label_info_mock):
        """
        Test the GmailManager on sending a new email message.
        """

        message_id = '15b33aad2c5dbe4a'

        # Mock the responses of the API calls.
        with open('lily/messaging/email/tests/data/send_email_message.json') as infile:
            json_obj = json.load(infile)
            send_email_message_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_label_info_SENT.json') as infile:
            json_obj = json.load(infile)
            get_label_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)

        # Prepare an email message that will be send out.
        email_outbox_message = EmailOutboxMessage.objects.create(
            subject="Mauris ex tortor, hendrerit non sem eu, mollis varius purus.",
            send_from=email_account,
            to=anyjson.dumps("user2@example.com"),
            cc=anyjson.dumps(None),
            bcc=anyjson.dumps(None),
            body=u"<html><body>In hac habitasse platea dictumst. Class aptent taciti sociosqu ad litora torquent "
                 u"per conubia nostra, per inceptos himenaeos. Ut aliquet elit sed augue bibendum malesuada."
                 u"But here also some weird characters ˚ø∆¨•ª¥¶†§ƒ√ª©∑´®º^˙∆ø˚˙∑•ª©®^º–π∆ªº^˙ª•ª¨©¶ ÖÄÖÄÖÄöäöäöäöä."
                 u"</body></html>",
            headers={},
            mapped_attachments=0,
            template_attachment_ids='',
            original_message_id='',
            tenant=self.user_obj.tenant
        )

        # Send the email message.
        manager.send_email_message(email_outbox_message.message())

        # Verify that is stored in the database as an email message.
        self.assertTrue(EmailMessage.objects.filter(account=email_account, message_id=message_id).exists(),
                        "Send message missing from the database.")

        # Verify that the email message has the correct labels.
        email_message = EmailMessage.objects.get(account=email_account, message_id=message_id)
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set([settings.GMAIL_LABEL_SENT]), "Send message mssing the SEND label.")

        # Verify that the email emssage has the correct thread id. Because the email message is not part of a thread,
        # the thread_id should be the same as the message_id.
        self.assertEqual(email_message.thread_id, message_id, "Message_id and thread_id should be the same.")

    @patch.object(GmailConnector, 'trash_email_message')
    @patch.object(GmailConnector, 'get_message_info')
    def test_trash_email_message(self, get_message_info_mock, trash_email_message_mock):
        """
        Test the GmailManager on trashing an email message.
        """
        message_id = '15af6279f554fd15'

        # Mock the responses of the API call.
        with open('lily/messaging/email/tests/data/trash_email_message_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            trash_email_message_mock.return_value = json_obj

        with open('lily/messaging/email/tests/data/get_message_info_{0}_trash.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()
        email_message = EmailMessageFactory.create(account=email_account, message_id=message_id)
        labels = [settings.GMAIL_LABEL_UNREAD, settings.GMAIL_LABEL_TRASH, settings.GMAIL_LABEL_INBOX]
        for label in labels:
            EmailLabelFactory.create(account=email_account, label_id=label)
        manager = GmailManager(email_account)

        manager.trash_email_message(email_message)

        # Verify that the email message is trashed by looking at the labels, ie. INBOX is not presnt and TRASH is.
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set([settings.GMAIL_LABEL_UNREAD, settings.GMAIL_LABEL_TRASH]))

    @patch.object(GmailConnector, 'get_message_info')
    def test_download_message_utf16(self, get_message_info_mock):
        """
        Test the GmailManager on downloading a utf-16 encoded message.
        """
        message_id = '161f6052954d7758'

        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            json_obj = json.load(infile)
            get_message_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()

        labels = [settings.GMAIL_LABEL_UNREAD, settings.GMAIL_LABEL_INBOX]
        for label in labels:
            EmailLabelFactory.create(account=email_account, label_id=label)

        manager = GmailManager(email_account)
        # Message isn't present in the db, so it will do a mocked API call.
        manager.download_message(message_id)

        # Verify that the email message is stored in the db.
        self.assertTrue(EmailMessage.objects.filter(account=email_account, message_id=message_id).exists())

    def test_cleanup(self):
        """
        Test if the GmailManager cleans up the right data.
        """

        # Initialze a manager.
        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)

        # Establish that the cleanup method up to test has actual data to cleanup.
        self.assertIsNotNone(manager.message_builder)
        self.assertIsNotNone(manager.label_builder)
        self.assertIsNotNone(manager.connector)
        self.assertIsNotNone(manager.email_account)

        manager.cleanup()

        # Verify that data is cleaned up.
        self.assertIsNone(manager.message_builder)
        self.assertIsNone(manager.label_builder)
        self.assertIsNone(manager.connector)
        self.assertIsNone(manager.email_account)

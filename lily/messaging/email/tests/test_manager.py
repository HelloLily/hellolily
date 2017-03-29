import json

from googleapiclient.discovery import build
from rest_framework.test import APITestCase

from lily.messaging.email.connector import GmailConnector
from lily.messaging.email.factories import GmailAccountFactory
from lily.messaging.email.manager import GmailManager
from lily.messaging.email.models.models import EmailAccount, EmailMessage, EmailLabel
from lily.messaging.email.services import GmailService
from lily.settings import settings
from lily.tests.utils import UserBasedTest

from mock import patch


class GmailManagerTests(UserBasedTest, APITestCase):
    """
    Class for unit testing the GmailManager.
    """

    def setUp(self):
        # Patch the creation of a Gmail API service without the need for authorized credentials.
        self.get_credentials_mock_patcher = patch('lily.messaging.email.connector.get_credentials')
        get_credentials_mock = self.get_credentials_mock_patcher.start()
        get_credentials_mock.return_value = None

        self.authorize_mock_patcher = patch.object(GmailService, 'authorize')
        authorize_mock = self.authorize_mock_patcher.start()
        authorize_mock.return_value = None

        self.build_service_mock_patcher = patch.object(GmailService, 'build_service')
        build_service_mock = self.build_service_mock_patcher.start()
        build_service_mock.return_value = build('gmail', 'v1')

    @classmethod
    def setUpTestData(cls):
        # Create a user, handled by UserBasedTest.
        super(GmailManagerTests, cls).setUpTestData()

        # Create an email account for the user.
        GmailAccountFactory.create(owner_id=cls.user_obj.id, tenant_id=cls.user_obj.tenant_id)

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
        no_call_download_email_message = sum(
            call[0][0] == 'download_email_message' for call in send_task_mock.call_args_list)
        no_call_full_sync_finished = sum(call[0][0] == 'full_sync_finished' for call in send_task_mock.call_args_list)

        self.assertEqual(no_call_download_email_message, len(messages))
        self.assertEqual(no_call_full_sync_finished, 1)

    @patch.object(GmailConnector, 'get_message_info')
    @patch.object(GmailManager, 'get_label')
    def test_download_message(self, get_label_mock, get_message_info_mock):
        """
        Test the GmailManager on downloading a message and that it is stored in the database.
        """
        with open('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json') as infile:
            json_obj = json.load(infile)

            get_message_info_mock.return_value = json_obj

        email_account = EmailAccount.objects.first()

        labels = [
            EmailLabel.objects.create(account=email_account, label_id=settings.GMAIL_LABEL_UNREAD,
                                      label_type=EmailLabel.LABEL_SYSTEM),
            EmailLabel.objects.create(account=email_account, label_id=settings.GMAIL_LABEL_IMPORTANT,
                                      label_type=EmailLabel.LABEL_SYSTEM),
            EmailLabel.objects.create(account=email_account, label_id='CATEGORY_PERSONAL',
                                      label_type=EmailLabel.LABEL_SYSTEM),
            EmailLabel.objects.create(account=email_account, label_id=settings.GMAIL_LABEL_INBOX,
                                      label_type=EmailLabel.LABEL_SYSTEM),
        ]
        get_label_mock.side_effect = labels

        manager = GmailManager(email_account)
        # Message isn't present in the db, so it will do a mocked API call.
        manager.download_message('15a6008a4baa65f3')

        # Verify that the email message is stored in the db.
        self.assertEqual(EmailMessage.objects.filter(account=email_account, message_id='15a6008a4baa65f3').exists(),
                         True)

        # Verify that the email message has the correct labels.
        email_message = EmailMessage.objects.get(account=email_account, message_id='15a6008a4baa65f3')
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set(['UNREAD', 'IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX']))

    @patch.object(GmailConnector, 'get_short_message_info')
    @patch.object(GmailConnector, 'get_message_info')
    def test_download_message_exists(self, get_message_info_mock, get_short_message_info_mock):
        """
        Test the GmailManager on updating an existing message.
        """
        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)

        labels = [
            EmailLabel.objects.create(account=email_account, label_id=settings.GMAIL_LABEL_UNREAD,
                                      label_type=EmailLabel.LABEL_SYSTEM),
            EmailLabel.objects.create(account=email_account, label_id=settings.GMAIL_LABEL_IMPORTANT,
                                      label_type=EmailLabel.LABEL_SYSTEM),
            EmailLabel.objects.create(account=email_account, label_id='CATEGORY_PERSONAL',
                                      label_type=EmailLabel.LABEL_SYSTEM),
            EmailLabel.objects.create(account=email_account, label_id=settings.GMAIL_LABEL_INBOX,
                                      label_type=EmailLabel.LABEL_SYSTEM),
        ]

        with open('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json') as infile:
            json_obj = json.load(infile)

            get_message_info_mock.return_value = json_obj

        # Patch get_label as a context manager so mocking is disabled after the message is downloaded for the first
        # time.
        with patch.object(GmailManager, 'get_label') as get_label_mock:
            get_label_mock.side_effect = labels

            # Message isn't present in the db, so it will do a mocked API call.
            manager.download_message('15a6008a4baa65f3')

        # The message with labels is now present in the database so downloading it again will only update it's labels.
        with open('lily/messaging/email/tests/data/get_short_message_info_15a6008a4baa65f3_archived.json') as infile:
            json_obj = json.load(infile)

            get_short_message_info_mock.return_value = json_obj

        try:
            manager.download_message('15a6008a4baa65f3')
        except StopIteration:
            # Because the email message is already in the database it should not do a (mocked) API call again.
            self.fail('StopIteration should have been raised.')

        # Verify that the email message has the correct labels after the updated short message info with the Inbox
        # label removed.
        email_message = EmailMessage.objects.get(account=email_account, message_id='15a6008a4baa65f3')
        email_message_labels = set(email_message.labels.all().values_list('label_id', flat=True))
        self.assertEqual(email_message_labels, set(['UNREAD', 'IMPORTANT', 'CATEGORY_PERSONAL']))

    @patch.object(GmailConnector, 'get_label_list')
    def test_sync_labels(self, get_label_list_mock):
        """
        Test the GmailManager on synchronizing the labels for the email account.
        """
        with open('lily/messaging/email/tests/data/get_label_list.json') as infile:
            json_obj = json.load(infile)

            labels = json_obj['labels']
            get_label_list_mock.return_value = labels

        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.sync_labels()

        # Verify that the correct number of labels are present in the database.
        self.assertEqual(EmailLabel.objects.filter(account=email_account).count(), len(labels))

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
        self.assertEqual(
            EmailLabel.objects.filter(account=email_account, label_id=settings.GMAIL_LABEL_INBOX).exists(), True)

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
        self.assertEqual(
            EmailLabel.objects.filter(account=email_account, label_id=settings.GMAIL_LABEL_INBOX).exists(), True)

        try:
            # Retrieve the same label again.
            manager.get_label(settings.GMAIL_LABEL_INBOX)
        except StopIteration:
            # Because the label is already in the database it should not do a (mocked) API call again.
            self.fail('StopIteration should have been raised.')

    def test_administer_full_sync_status_true(self):
        """
        Test the GmailManager on setting the full sync status to finished on the email account.
        """
        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.administer_full_sync_status(True)

        self.assertEqual(email_account.full_sync_finished, True)
        self.assertEqual(email_account.sync_failure_count, 0)

    def test_administer_full_sync_status_false(self):
        """
        Test the GmailManager on setting the full sync status to not finished on the email account.
        """
        email_account = EmailAccount.objects.first()
        manager = GmailManager(email_account)
        manager.administer_full_sync_status(False)

        self.assertEqual(email_account.full_sync_finished, False)
        self.assertEqual(email_account.sync_failure_count, 0)

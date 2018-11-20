import json
from django.test import TestCase

from googleapiclient.discovery import build
from lily.tests.utils import UserBasedTest, get_dummy_credentials
from lily.messaging.email.factories import EmailAccountFactory
from lily.messaging.email.services import GmailService
from lily.messaging.email.connector import GmailConnector
from lily.messaging.email.builders.utils import get_attachments_from_payload, get_body_html_from_payload

from mock import patch


class EmailUtilsTestCase(UserBasedTest, TestCase):
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

        # Reset changes made to the email account in a test.
        self.email_account.refresh_from_db()

    @classmethod
    def setUpTestData(cls):
        # Create a user, handled by UserBasedTest.
        super(EmailUtilsTestCase, cls).setUpTestData()

        # Create an email account for the user.
        cls.email_account = EmailAccountFactory.create(owner=cls.user_obj, tenant=cls.user_obj.tenant)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    def mock_get_message_info(self, to_mock, message_id):
        with open('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id)) as infile:
            to_mock.return_value = json.load(infile)

    def mock_get_attachment(self, to_mock, message_id):
        with open('lily/messaging/email/tests/data/get_attachment_{0}.json'.format(message_id)) as infile:
            to_mock.return_value = json.load(infile)

    @patch.object(GmailConnector, 'get_attachment')
    @patch.object(GmailConnector, 'get_message_info')
    def test_extracting_attachment(self, get_message_info_mock, get_attachment_mock):
        message_id = '16740205f39700d1'
        self.mock_get_message_info(get_message_info_mock, message_id)
        self.mock_get_attachment(get_attachment_mock, message_id)

        connector = GmailConnector(self.email_account)
        message_info = connector.get_message_info(message_id)

        payload = message_info['payload']

        body_html = get_body_html_from_payload(payload, message_id)
        attachments = get_attachments_from_payload(payload, body_html, message_id, [], connector)

        get_message_info_mock.assert_called_once()
        get_attachment_mock.assert_called_once()

        self.assertEqual(len(attachments), 1)

    @patch.object(GmailConnector, 'get_attachment')
    @patch.object(GmailConnector, 'get_message_info')
    def test_extracting_inline_attachment(self, get_message_info_mock, get_attachment_mock):
        message_id = '16755866c49c1423'
        self.mock_get_message_info(get_message_info_mock, message_id)
        self.mock_get_attachment(get_attachment_mock, message_id)

        connector = GmailConnector(self.email_account)
        message_info = connector.get_message_info(message_id)

        payload = message_info['payload']

        body_html = get_body_html_from_payload(payload, message_id)
        attachments = get_attachments_from_payload(payload, body_html, message_id, [], connector)

        get_message_info_mock.assert_called_once()
        get_attachment_mock.assert_called_once()

        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments[0].inline)

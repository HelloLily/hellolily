import json

from googleapiclient.discovery import build
from googleapiclient.http import HttpMock
from oauth2client.client import HttpAccessTokenRefreshError
from rest_framework.test import APITestCase

from lily.messaging.email.connector import GmailConnector, FailedServiceCallException
from lily.messaging.email.factories import GmailAccountFactory
from lily.messaging.email.models.models import EmailAccount
from lily.messaging.email.services import GmailService
from lily.tests.utils import UserBasedTest, get_dummy_credentials

from mock import MagicMock, patch


class GmailConnectorTests(UserBasedTest, APITestCase):
    """
    Class for unit testing the GmailConnector.
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
        super(GmailConnectorTests, cls).setUpTestData()

        # Create an email account for the user.
        GmailAccountFactory.create(owner_id=cls.user_obj.id, tenant_id=cls.user_obj.tenant_id)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    @patch.object(GmailService, '_get_http')
    def test_execute_service_call(self, get_http_mock):
        """
        Test if the execute service call returns the content of the json file.
        """
        # Mock the http instance.
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json',
                                  {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)

        # Execute service call.
        response = connector.execute_service_call(
            connector.gmail_service.service.users().messages().list(
                userId='me',
                quotaUser=email_account.id,
                q='!in:chats',
            ))

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/all_message_id_list_single_page.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

    @patch.object(GmailService, '_get_http')
    def test_execute_service_call_rate_limit_exceeded_once(self, get_http_mock):
        """
        Test if the execute service call returns the content of the json file after one rate limit error.
        """
        mock_api_calls = [
            # Simulate one rateLimitExceeded error.
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
        ]

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)

        # Execute service call.
        response = connector.execute_service_call(
            connector.gmail_service.service.users().messages().list(
                userId='me',
                quotaUser=email_account.id,
                q='!in:chats',
            ))

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/all_message_id_list_single_page.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

    @patch.object(GmailService, '_get_http')
    def test_execute_service_call_failed_service_call_exception(self, get_http_mock):
        """
        Test if the execute service call raises an exception after it fails after six rate limit errors.
        """
        mock_api_calls = [
            # Simulate one FailedServiceCallException by getting six times a rateLimitExceeded error.
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
        ]

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)

        try:
            # Execute service call.
            connector.execute_service_call(
                connector.gmail_service.service.users().messages().list(
                    userId='me',
                    quotaUser=email_account.id,
                    q='!in:chats',
                ))
            self.fail('FailedServiceCallException should have been raised.')
        except FailedServiceCallException:
            pass

    @patch.object(GmailService, 'execute_service')
    def test_execute_service_call_http_access_token_refresh_error(self, execute_service_mock):
        """
        Test if the execute service call raises an exception after it isn't able to get a correct access token
        and correctly deauthorizes the email account.
        """
        # Let the mocked execute service call raise an error.
        execute_service_mock.side_effect = HttpAccessTokenRefreshError()

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        try:
            # Execute service call.
            connector.execute_service_call(
                connector.gmail_service.service.users().messages().list(
                    userId='me',
                    quotaUser=email_account.id,
                    q='!in:chats',
                ))
            self.fail('HttpAccessTokenRefreshError should have been raised.')
        except HttpAccessTokenRefreshError:
            pass

        self.assertFalse(email_account.is_authorized, "Email account shouldn't be authorized.")

    @patch.object(GmailService, '_get_http')
    def test_get_all_message_id_list(self, get_http_mock):
        """
        Test the GmailConnector in retrieving all message id's without errors on the API call.
        """
        mock_api_calls = [
            # Retrieve the history_id.
            HttpMock('lily/messaging/email/tests/data/get_history_id.json', {'status': '200'}),
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
        ]

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_account = EmailAccount.objects.first()

        # Retrieve all messages.
        connector = GmailConnector(email_account)
        messages = connector.get_all_message_id_list()

        # Verify that all messages are retrieved and that the history id is set correct,
        self.assertEqual(len(messages), 10, "%d Messages found, it should be %d." % (len(messages), 10))
        self.assertEqual(connector.history_id, u'8095',
                         "History id %s is incorrect, it should be %s." % (connector.history_id, u'8095'))

    @patch.object(GmailService, '_get_http')
    def test_get_all_message_id_list_paged(self, get_http_mock):
        """
        Test the GmailConnector in retrieving all message id's without errors on the API call.
        Messages are paged and need two API calls.
        """
        mock_api_calls = [
            # Retrieve the history_id.
            HttpMock('lily/messaging/email/tests/data/get_history_id.json', {'status': '200'}),
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_paged_1.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_paged_2.json', {'status': '200'}),
        ]

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_account = EmailAccount.objects.first()

        # Retrieve all messages.
        connector = GmailConnector(email_account)
        messages = connector.get_all_message_id_list()

        # Verify that all messages are retrieved and that the history id is set correct,
        self.assertEqual(len(messages), 10, "%d Messages found, it should be %d." % (len(messages), 10))
        self.assertEqual(connector.history_id, u'8095',
                         "History id %s is incorrect, it should be %s." % (connector.history_id, 8095))

    @patch.object(GmailConnector, 'execute_service_call')
    def test_get_all_message_id_list_http_access_token_refresh_error(self, execute_service_call_mock):
        """
        Test the GmailConnector in retrieving all message id's with a HttpAccessTokenRefreshError on the API call.
        """
        execute_service_call_mock.side_effect = HttpAccessTokenRefreshError()

        email_account = EmailAccount.objects.first()

        messages = None
        connector = GmailConnector(email_account)

        # Retrieve all messages.
        try:
            messages = connector.get_all_message_id_list()
            self.fail('HttpAccessTokenRefreshError should have been raised.')
        except HttpAccessTokenRefreshError:
            pass

        # Verify that no messages are retrieved and that the history id is not set,
        self.assertIsNone(messages)
        self.assertIsNone(connector.history_id)

    @patch.object(GmailConnector, 'execute_service_call')
    def test_get_all_message_id_list_failed_service_call_error(self, execute_service_call_mock):
        """
        Test the GmailConnector in retrieving all message id's with a FailedServiceCallException on the API call.
        """
        execute_service_call_mock.side_effect = FailedServiceCallException()

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)

        # Retrieve all messages.
        messages = None
        try:
            messages = connector.get_all_message_id_list()
            self.fail('FailedServiceCallException should have been raised.')
        except FailedServiceCallException:
            pass

        # Verify that no messages are retrieved and that the history id is not set,
        self.assertIsNone(messages)
        self.assertIsNone(connector.history_id)

    @patch.object(GmailService, '_get_http')
    def test_get_message_info(self, get_http_mock):
        """
        Test the GmailConnector in retrieving the info of a single email message.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json',
                                  {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        response = connector.get_message_info('15a6008a4baa65f3')

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

        # Verify that the history id is retrieved from the get API response.
        self.assertEqual(connector.history_id, u'5948')

    @patch.object(GmailService, '_get_http')
    def test_get_label_info(self, get_http_mock):
        """
        Test the GmailConnector in retrieving the info of a single label.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/get_label_info_INBOX.json', {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        response = connector.get_label_info('INBOX')

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/get_label_info_INBOX.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

    @patch.object(GmailService, '_get_http')
    def test_get_label_list(self, get_http_mock):
        """
        Test the GmailConnector in retrieving the list of the available labels.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/get_label_list.json', {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        response = connector.get_label_list()

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/get_label_list.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj['labels'])

    @patch.object(GmailService, '_get_http')
    def test_get_short_message_info(self, get_http_mock):
        """
        Test the GmailConnector in retrieving the short message info for a specific email message.
        """
        get_http_mock.side_effect = MagicMock(return_value=HttpMock(
            'lily/messaging/email/tests/data/get_short_message_info_15a6008a4baa65f3_archived.json',
            {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        response = connector.get_short_message_info('15a6008a4baa65f3')

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/get_short_message_info_15a6008a4baa65f3_archived.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

    @patch.object(GmailService, '_get_http')
    def test_get_history(self, get_http_mock):
        """
        Test the GmailConnector in retrieving the history updates.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/get_history_archived.json', {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        response = connector.get_history()

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/get_history_archived.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj['history'])

        # Verify that the history is updated with the one from the API response.
        self.assertEqual(connector.history_id, u'8170')

    @patch.object(GmailService, '_get_http')
    def test_save_history_id(self, get_http_mock):
        """
        Test the GmailConnector in saving the updated historty id to the email account.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/get_history_archived.json', {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        # First do a history update, so a new history id is retreived.
        connector.get_history()
        # Save the history id to the email account.
        connector.save_history_id()

        # Verify that the history is indeed saved on the email account.
        email_account.refresh_from_db()
        self.assertEqual(email_account.history_id, 8170)

    @patch.object(GmailService, '_get_http')
    def test_get_history_id(self, get_http_mock):
        """
        Test the GmailConnector in retrieving the history id.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/get_history_id.json', {'status': '200'}))

        email_account = EmailAccount.objects.first()

        connector = GmailConnector(email_account)
        response = connector.get_history_id()

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/get_history_id.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

    @patch.object(GmailService, '_get_http')
    def test_send_email_message(self, get_http_mock):
        """
        Test the GmailConnector on sending a email message.
        """
        get_http_mock.side_effect = MagicMock(
            return_value=HttpMock('lily/messaging/email/tests/data/send_email_message.json', {'status': '200'}))

        email_account = EmailAccount.objects.first()
        email_outbox_message = """Content-Type: multipart/related;
 boundary="===============0529811256475331541=="
MIME-Version: 1.0
Subject: Mauris ex tortor, hendrerit non sem eu, mollis varius purus.
From: "Firstname Lastname" <user1@example.com>
To: user2@example.com

--===============0529811256475331541==
Content-Type: multipart/alternative;
 boundary="===============6835128886458232912=="
MIME-Version: 1.0

--===============6835128886458232912==
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 7bit


In hac habitasse platea dictumst. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos
himenaeos. Ut aliquet elit sed augue bibendum malesuada.

--===============6835128886458232912==
MIME-Version: 1.0
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 7bit

<html><body><br/>In hac habitasse platea dictumst. Class aptent taciti sociosqu ad litora torquent per conubia nostra,
per inceptos himenaeos. Ut aliquet elit sed augue bibendum malesuada.</body></html>
--===============6835128886458232912==--

--===============0529811256475331541==--"""

        connector = GmailConnector(email_account)
        response = connector.send_email_message(email_outbox_message)

        # Verify that the service call returned the correct json object.
        with open('lily/messaging/email/tests/data/send_email_message.json') as infile:
            json_obj = json.load(infile)
            self.assertEqual(response, json_obj)

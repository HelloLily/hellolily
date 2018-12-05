# -*- coding: utf-8 -*-
import json
from django.test import TestCase

from googleapiclient.discovery import build
from lily.tests.utils import UserBasedTest, EmailBasedTest, get_dummy_credentials
from lily.messaging.email.services import GmailService
from lily.messaging.email.connector import GmailConnector
from lily.messaging.email.utils import get_formatted_email_body
from lily.messaging.email.builders.utils import get_attachments_from_payload, get_body_html_from_payload

from mock import patch


class EmailUtilsTestCase(UserBasedTest, EmailBasedTest, TestCase):
    def setUp(self):
        super(EmailUtilsTestCase, self).setUp()
        super(EmailUtilsTestCase, self).setupEmailMessage()

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
        attachments = get_attachments_from_payload(payload, body_html, message_id, connector)

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
        attachments = get_attachments_from_payload(payload, body_html, message_id, connector)

        get_message_info_mock.assert_called_once()
        get_attachment_mock.assert_called_once()

        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments[0].inline)

    def get_expected_email_body_parts(self, subject='Simple Subject',
                                      recipient='Simple Name &lt;someuser@example.com&gt;'):
        expected_body_html_part_one = (
            '<br /><br /><hr />---------- Forwarded message ---------- <br />'
            'From: user1@example.com<br/>'
            'Date: '
        )
        expected_body_html_part_two = (
            '<br/>Subject: {}<br/>'
            'To: {}<br />'
        ).format(subject, recipient)

        return expected_body_html_part_one, expected_body_html_part_two

    def test_get_formatted_email_body_action_forward(self):
        body_html = get_formatted_email_body('forward', self.email_message)

        part_one, part_two = self.get_expected_email_body_parts()

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_email_body_action_forward_complex_subject(self):
        self.email_message.subject = 'Complex Sübject'
        body_html = get_formatted_email_body('forward', self.email_message)

        part_one, part_two = self.get_expected_email_body_parts(self.email_message.subject)

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_email_body_action_forward_complex_recipient(self):
        received_by = self.email_message.received_by.first()
        received_by.name = 'Cömplicated Name'
        received_by.save()
        body_html = get_formatted_email_body('forward', self.email_message)

        recipient = 'Cömplicated Name &lt;someuser@example.com&gt;'
        part_one, part_two = self.get_expected_email_body_parts(recipient=recipient)

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

    def test_get_formatted_email_body_action_forward_simple(self):
        self.email_message.subject = 'Simple Subject'
        received_by = self.email_message.received_by.first()
        received_by.name = None
        received_by.email_address = 'support@ümail.nl'
        received_by.save()

        body_html = get_formatted_email_body('forward', self.email_message)

        part_one, part_two = self.get_expected_email_body_parts(recipient=received_by.email_address)

        self.assertIn(part_one, body_html)
        self.assertIn(part_two, body_html)

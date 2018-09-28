import anyjson
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock
from oauth2client.client import HttpAccessTokenRefreshError
from rest_framework.test import APITestCase

from lily.celery import app
from lily.messaging.email.factories import EmailAccountFactory
from lily.messaging.email.models.models import EmailAccount, EmailMessage, EmailOutboxMessage
from lily.messaging.email.services import GmailService
from lily.messaging.email.tasks import synchronize_email_account_scheduler, send_message
from lily.tests.utils import UserBasedTest, get_dummy_credentials

from mock import patch


class EmailTests(UserBasedTest, APITestCase):
    """
    Class for integrated email testing.

    API calls to Google are mocked.
    """

    verify_label_data_default = {
        # label: [available, total count, unread count],
        'all_mail': [True, 10, 6],  # Mail without trash, spam or chat.
        settings.GMAIL_LABEL_INBOX: [True, 5, 4],
        settings.GMAIL_LABEL_UNREAD: [True, 6, 6],
        settings.GMAIL_LABEL_STAR: [True, 1, 1],
        settings.GMAIL_LABEL_SENT: [True, 2, 0],
        settings.GMAIL_LABEL_DRAFT: [True, 1, 0],
        settings.GMAIL_LABEL_SPAM: [True, 0, 0],
        settings.GMAIL_LABEL_TRASH: [True, 0, 0],
        'Label_1': [True, 3, 2],
        'Label_2': [True, 2, 2],
    }

    verify_label_availability_default = {
        # label: available,
        settings.GMAIL_LABEL_INBOX: True,
        settings.GMAIL_LABEL_UNREAD: True,
        settings.GMAIL_LABEL_STAR: False,
        settings.GMAIL_LABEL_SENT: False,
        settings.GMAIL_LABEL_DRAFT: False,
        settings.GMAIL_LABEL_SPAM: False,
        settings.GMAIL_LABEL_TRASH: False,
        'Label_1': False,
        'Label_2': False,
    }

    mock_api_calls_default = [
        # Retrieve the history_id.
        HttpMock('lily/messaging/email/tests/data/get_history_id.json', {'status': '200'}),
        # Retrieve a list of all the messages in the email box.
        HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
        # Retrieve all 10 email messages and their labels.
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_INBOX.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a600737124149d.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_DRAFT.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a600682d97904e.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_Label_2.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a60067ef5e0bf9.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_STARRED.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a600543e10c8e4.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a60053f67f5de4.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_Label_1.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a60053dea565fa.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a60044bb3e2a7a.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a60025b255c626.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_label_info_SENT.json', {'status': '200'}),
        HttpMock('lily/messaging/email/tests/data/get_message_info_15a6001f325c4e9d.json', {'status': '200'}),
    ]

    def setUp(self):

        def send_task(name, args=(), kwargs={}, **opts):
            # https://github.com/celery/celery/issues/581
            task = app.tasks[name]
            return task.apply(args, kwargs, **opts)

        # Let Celery execute the tasks immediately.
        app.send_task = send_task
        app.conf.update(CELERY_ALWAYS_EAGER=True)

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
        super(EmailTests, cls).setUpTestData()

        # Create an email account for the user.
        cls.email_account = EmailAccountFactory.create(owner=cls.user_obj, tenant=cls.user_obj.tenant)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    def test_full_synchronize_single_page_history(self):
        """
        Do a full synchronize of one email account, without simulated backend errors. The history spans one API call.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        self._test_full_synchronize(mock_api_calls=self.mock_api_calls_default,
                                    label_data_after=self.verify_label_data_default)

    def test_full_synchronize_paged_history(self):
        """
        Do a full synchronize of one email account, without simulated backend errors. The history spans more than one
        API call.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = [
            # Retrieve the history_id.
            HttpMock('lily/messaging/email/tests/data/get_history_id.json', {'status': '200'}),
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_paged_1.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_paged_2.json', {'status': '200'}),
            # Retrieve all 10 email messages and their labels.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_INBOX.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a600737124149d.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_DRAFT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a600682d97904e.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_Label_2.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60067ef5e0bf9.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_STARRED.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a600543e10c8e4.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60053f67f5de4.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_Label_1.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60053dea565fa.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60044bb3e2a7a.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60025b255c626.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_SENT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6001f325c4e9d.json', {'status': '200'}),
        ]

        self._test_full_synchronize(mock_api_calls=mock_api_calls, label_data_after=self.verify_label_data_default)

    def test_full_synchronize_rate_limit_exceeded_once(self):
        """
        Do a full synchronize of one email account, with a single simulated rateLimitExceeded error.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = [
            # Retrieve the history_id.
            HttpMock('lily/messaging/email/tests/data/get_history_id.json', {'status': '200'}),
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
            # Retrieve all 10 email messages and their labels.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_INBOX.json', {'status': '200'}),
            # Simulate one rateLimitExceeded error.
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            # And continue with syncing after a single error.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a600737124149d.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_DRAFT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a600682d97904e.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_Label_2.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60067ef5e0bf9.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_STARRED.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a600543e10c8e4.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60053f67f5de4.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_Label_1.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60053dea565fa.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60044bb3e2a7a.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a60025b255c626.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_SENT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6001f325c4e9d.json', {'status': '200'}),
        ]

        self._test_full_synchronize(mock_api_calls=mock_api_calls, label_data_after=self.verify_label_data_default)

    @patch.object(GmailService, '_get_http')
    def test_full_synchronize_failed_service_call_exception(self, get_http_mock):
        """
        Do a full synchronize of one email account, with six simulated rateLimitExceeded errors which result in a
        FailedServiceCallException. After that the account stops syncing.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """
        email_account = EmailAccount.objects.first()

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

        # Calling the scheduler once, with a missing history_id for the email account, it will effectively do a full
        # initial synchronize.
        # So make sure history_id is indeed missing and that the email account is in the right state.
        self._verify_email_account_state(email_account=email_account, authorized=True, history_id=None,
                                         is_syncing=False)

        synchronize_email_account_scheduler()

        # Retrieve the updated email account.
        email_account.refresh_from_db()

        # Verify the existence of labels and the number (un)read emails per label and archived email.
        verify_label_data = {
            # label: [available, total count, unread count],
            'all_mail': [False, 0, 0],  # Mail without trash, spam or chat.
            settings.GMAIL_LABEL_INBOX: [False, 0, 0],
            settings.GMAIL_LABEL_UNREAD: [False, 0, 0],
            settings.GMAIL_LABEL_STAR: [False, 0, 0],
            settings.GMAIL_LABEL_SENT: [False, 0, 0],
            settings.GMAIL_LABEL_DRAFT: [False, 0, 0],
            settings.GMAIL_LABEL_SPAM: [False, 0, 0],
            settings.GMAIL_LABEL_TRASH: [False, 0, 0],
            'Label_1': [False, 0, 0],
            'Label_2': [False, 0, 0],
        }
        self._label_test(email_account, verify_label_data)

        self._verify_email_account_state(email_account=email_account, authorized=False, history_id=None,
                                         is_syncing=False)

    @patch.object(GmailService, 'execute_service')
    def test_full_synchronize_http_access_token_refresh_error(self, execute_service_mock):
        """
        Do a full synchronize of one email account, with a simulated HttpAccessTokenRefreshError error.

        Verifies that the email account is unauthorized and that there are no labels and emails stored in the database.
        """

        # Mock the service execute call with a HttpAccessTokenRefreshError.
        execute_service_mock.side_effect = HttpAccessTokenRefreshError()

        email_account = EmailAccount.objects.first()

        # Calling the scheduler once, with a missing history_id for the email account, it will effectively do a full
        # initial synchronize.
        # So make sure history_id is indeed missing and that the email account is in the right state.
        self._verify_email_account_state(email_account=email_account, authorized=True, history_id=None,
                                         is_syncing=False)

        synchronize_email_account_scheduler()

        # Retrieve the updated email account.
        email_account.refresh_from_db()

        # Verify the existence of labels and the number (un)read emails per label and archived email.
        verify_label_data = {
            # label: [available, total count, unread count],
            'all_mail': [False, 0, 0],  # Mail without trash, spam or chat.
            settings.GMAIL_LABEL_INBOX: [False, 0, 0],
            settings.GMAIL_LABEL_UNREAD: [False, 0, 0],
            settings.GMAIL_LABEL_STAR: [False, 0, 0],
            settings.GMAIL_LABEL_SENT: [False, 0, 0],
            settings.GMAIL_LABEL_DRAFT: [False, 0, 0],
            settings.GMAIL_LABEL_SPAM: [False, 0, 0],
            settings.GMAIL_LABEL_TRASH: [False, 0, 0],
            'Label_1': [False, 3, 2],
            'Label_2': [False, 2, 2],
        }
        self._label_test(email_account, verify_label_data)

        self._verify_email_account_state(email_account=email_account, authorized=False, history_id=None,
                                         is_syncing=False)

    def test_incremental_synchronize_no_history(self):
        """
        Do a full synchronize and one succesive history update on one email account, without simulated backend errors.
        The history has no updates.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_page_1_empty.json', {'status': '200'}),
        ]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls,
                                           label_data_after=self.verify_label_data_default)

    def test_incremental_synchronize_label_added(self):
        """
        Do a full synchronize and one succesive history update on one email account. A label is added to one email
        message.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a6008a4baa65f3'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_label_added.json', {'status': '200'}),
            # Retrieve the message to which the single label was added.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_label_added.json'.format(message_id),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['Label_1'] = [True, 4, 3]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8134)

        # Verify that the label mutation is applied on the correct email message.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels['Label_1'] = True

        self._test_email_message(message_id, label_data=verify_labels)

    def test_incremental_synchronize_label_added_multiple(self):
        """
        Do a full synchronize and one succesive history update on one email account. A label is added to two email
        messages.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id_1 = '15a60067ef5e0bf9'
        message_id_2 = '15a600682d97904e'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_label_added_multiple.json', {'status': '200'}),
            # Retrieve the messages to which the label was added.
            HttpMock(
                'lily/messaging/email/tests/data/get_short_message_info_{0}_label_added.json'.format(message_id_2),
                {'status': '200'}),
            HttpMock(
                'lily/messaging/email/tests/data/get_short_message_info_{0}_label_added.json'.format(message_id_1),
                {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['Label_1'] = [True, 5, 4]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=9530)

        # Verify that the label mutation is applied on the correct email messages.
        verify_labels = self.verify_label_availability_default.copy()

        verify_labels['Label_1'] = True
        verify_labels[settings.GMAIL_LABEL_STAR] = True
        self._test_email_message(message_id_1, label_data=verify_labels)

        verify_labels['Label_2'] = True
        verify_labels[settings.GMAIL_LABEL_STAR] = False
        self._test_email_message(message_id_2, label_data=verify_labels)

    def test_incremental_synchronize_label_removed(self):
        """
        Do a full synchronize and one succesive history update on one email account. A label is remove from a single
        message.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a6008a4baa65f3'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_label_removed.json', {'status': '200'}),
            # Retrieve the message to which the single label was removed.
            HttpMock(
                'lily/messaging/email/tests/data/get_short_message_info_{0}_label_removed.json'.format(message_id),
                {'status': '200'}),
        ]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls,
                                           label_data_after=self.verify_label_data_default, history_id_after=8142)

        # Verify that the label mutation is applied on the correct email message.
        verify_labels = self.verify_label_availability_default.copy()

        self._test_email_message(message_id, label_data=verify_labels)

    def test_incremental_synchronize_label_removed_multiple(self):
        """
        Do a full synchronize and one succesive history update on one email account. A label is removed for two email
        messages.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id_1 = '15a600682d97904e'
        message_id_2 = '15a60053f67f5de4'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_label_removed_multiple.json', {'status': '200'}),
            # Retrieve the messages to which the single label was removed.
            HttpMock(
                'lily/messaging/email/tests/data/get_short_message_info_{0}_label_removed.json'.format(message_id_1),
                {'status': '200'}),
            HttpMock(
                'lily/messaging/email/tests/data/get_short_message_info_{0}_label_removed.json'.format(message_id_2),
                {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['Label_2'] = [True, 0, 0]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=9545)

        # Verify that the label mutation is applied on the correct email messages.
        verify_labels = self.verify_label_availability_default.copy()
        self._test_email_message(message_id_1, label_data=verify_labels)
        verify_labels['Label_1'] = True
        self._test_email_message(message_id_2, label_data=verify_labels)

    def test_incremental_synchronize_archived(self):
        """
        Do a full synchronize and one succesive history update on one email account.  Two email messages are archived.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id_1 = '15a6008a4baa65f3'
        message_id_2 = '15a600682d97904e'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_archived.json', {'status': '200'}),
            # Retrieve the archived messages.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_archived.json'.format(message_id_1),
                     {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_archived.json'.format(message_id_2),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 10, 8]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 3, 2]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8170)

        # Verify that the correct email messages are archived.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_INBOX] = False

        self._test_email_message(message_id_1, label_data=verify_labels)
        verify_labels['Label_2'] = True
        self._test_email_message(message_id_2, label_data=verify_labels)

    def test_incremental_synchronize_starred(self):
        """
        Do a full synchronize and one succesive history update on one email account. Two email messages are starred.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id_1 = '15a6008a4baa65f3'
        message_id_2 = '15a600682d97904e'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_starred.json', {'status': '200'}),
            # Retrieve the starred messages.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_starred.json'.format(message_id_1),
                     {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_starred.json'.format(message_id_2),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data[settings.GMAIL_LABEL_STAR] = [True, 3, 3]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8336)

        # Verify that the correct email messages are starred.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_STAR] = True

        self._test_email_message(message_id_1, label_data=verify_labels)
        verify_labels['Label_2'] = True
        self._test_email_message(message_id_2, label_data=verify_labels)

    def test_incremental_synchronize_label_read(self):
        """
        Do a full synchronize and one succesive history update on one email account. Two email messages are marked as
        read.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id_1 = '15a6008a4baa65f3'
        message_id_2 = '15a600682d97904e'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_read.json', {'status': '200'}),
            # Retrieve the messages which were read.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_read.json'.format(message_id_1),
                     {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_read.json'.format(message_id_2),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 10, 4]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 5, 2]
        verify_label_data[settings.GMAIL_LABEL_UNREAD] = [True, 4, 4]
        verify_label_data['Label_2'] = [True, 2, 1]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8427)

        # Verify that the correct email message is marked as read.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_UNREAD] = False

        self._test_email_message(message_id_1, label_data=verify_labels)
        verify_labels['Label_2'] = True
        self._test_email_message(message_id_2, label_data=verify_labels)

    def test_incremental_synchronize_label_unread(self):
        """
        Do a full synchronize and one succesive history update on one email account. An email message ise marked as
        unread.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a60044bb3e2a7a'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_unread.json', {'status': '200'}),
            # Retrieve the message which were marked unread.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_unread.json'.format(message_id),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 10, 7]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 5, 5]
        verify_label_data[settings.GMAIL_LABEL_UNREAD] = [True, 7, 7]
        verify_label_data['Label_1'] = [True, 3, 3]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8502)

        # Verify that the correct email message is unmarked as read.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_UNREAD] = True
        verify_labels['Label_1'] = True

        self._test_email_message(message_id, label_data=verify_labels)

    def test_incremental_synchronize_label_spam(self):
        """
        Do a full synchronize and one succesive history update on one email account. An email message is marked as
        spam.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a6008a4baa65f3'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_spam.json', {'status': '200'}),
            # Retrieve the message which were marked spam.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_spam.json'.format(message_id),
                     {'status': '200'}),
            # Retrieve the corresponding spam label.
            HttpMock('lily/messaging/email/tests/data/get_label_info_SPAM.json', {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 9, 6]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 4, 3]
        verify_label_data[settings.GMAIL_LABEL_UNREAD] = [True, 6, 6]
        verify_label_data[settings.GMAIL_LABEL_SPAM] = [True, 1, 1]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8792)

        # Verify that the correct email message is marked as spam.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_SPAM] = True
        verify_labels[settings.GMAIL_LABEL_INBOX] = False

        self._test_email_message(message_id, label_data=verify_labels)

    def test_incremental_synchronize_label_unspam(self):
        """
        Do a full synchronize and one succesive history update on one email account. An email message is unmarked as
        spam.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a6008a4baa65f3'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_unspam.json', {'status': '200'}),
            # Retrieve the message which were unmarked as spam.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_unspam.json'.format(message_id),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=8851)

        # Verify that the correct email message is unmarked as spam.
        verify_labels = self.verify_label_availability_default.copy()

        self._test_email_message(message_id, label_data=verify_labels)

    def test_incremental_synchronize_trash(self):
        """
        Do a full synchronize and one succesive history update on one email account. An email message is trashed.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a6008a4baa65f3'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_trashed.json', {'status': '200'}),
            # Retrieve the trashed message.
            HttpMock('lily/messaging/email/tests/data/get_short_message_info_{0}_trashed.json'.format(message_id),
                     {'status': '200'}),
            # Retrieve the corresponding trash label.
            HttpMock('lily/messaging/email/tests/data/get_label_info_TRASH.json', {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 9, 5]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 4, 3]
        verify_label_data[settings.GMAIL_LABEL_TRASH] = [True, 1, 1]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=9616)

        # Verify that the correct email messages are trashed.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_INBOX] = False
        verify_labels[settings.GMAIL_LABEL_TRASH] = True

        self._test_email_message(message_id, label_data=verify_labels)

    def test_incremental_synchronize_delete(self):
        """
        Do a full synchronize and one succesive history update on one email account. An email message is deleted.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id = '15a6008a4baa65f3'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_delete.json', {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 9, 5]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 4, 3]
        verify_label_data[settings.GMAIL_LABEL_UNREAD] = [True, 5, 5]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=9733)

        # Verify that the correct email message is gone.
        self.assertFalse(EmailMessage.objects.filter(message_id=message_id).exists())

    def test_incremental_synchronize_new_messages(self):
        """
        Do a full synchronize and one succesive history update on one email account. Two new email messages are
        received.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly. Also verify that the history update is
        reflected correctly on the right email message.
        """
        message_id_1 = '15af6279f554fd15'
        message_id_2 = '15af6279e8b72e9c'

        mock_api_calls = self.mock_api_calls_default + [
            # Retrieve the history updates since the first full synchronisation.
            HttpMock('lily/messaging/email/tests/data/get_history_new_messages.json', {'status': '200'}),
            # Retrieve the new messages.
            HttpMock('lily/messaging/email/tests/data/get_message_info_{0}_new.json'.format(message_id_1),
                     {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_{0}_new.json'.format(message_id_2),
                     {'status': '200'}),
        ]

        # Update the label data matching the mutation that was in the history update.
        verify_label_data = self.verify_label_data_default.copy()
        verify_label_data['all_mail'] = [True, 12, 8]
        verify_label_data[settings.GMAIL_LABEL_INBOX] = [True, 7, 6]
        verify_label_data[settings.GMAIL_LABEL_UNREAD] = [True, 8, 8]

        self._test_incremental_synchronize(mock_api_calls=mock_api_calls, label_data_after=verify_label_data,
                                           history_id_after=9841)

        # Verify that the label mutation is applied on the correct email messages.
        verify_labels = self.verify_label_availability_default.copy()

        self._test_email_message(message_id_1, label_data=verify_labels)
        self._test_email_message(message_id_2, label_data=verify_labels)

    @patch.object(GmailService, '_get_http')
    def test_send_message(self, get_http_mock):
        """
        Do a full synchronize of one email account. Afterwards send out an email message.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """
        message_id = '15b33aad2c5dbe4a'

        mock_api_calls = self.mock_api_calls_default + [
            HttpMock('lily/messaging/email/tests/data/send_email_message.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_message_info_{0}.json'.format(message_id),
                     {'status': '200'}),
        ]

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_outbox_message = EmailOutboxMessage.objects.create(
            subject="Mauris ex tortor, hendrerit non sem eu, mollis varius purus.",
            send_from=self.email_account,
            to=anyjson.dumps("user2@example.com"),
            cc=anyjson.dumps(None),
            bcc=anyjson.dumps(None),
            body="<html><body><br/>In hac habitasse platea dictumst. Class aptent taciti sociosqu ad litora torquent "
                 "per conubia nostra, per inceptos himenaeos. Ut aliquet elit sed augue bibendum malesuada."
                 "</body></html>",
            headers={},
            mapped_attachments=0,
            template_attachment_ids='',
            original_message_id='',
            tenant=self.user_obj.tenant
        )

        synchronize_email_account_scheduler()

        # Call the task to send out the email message.
        send_message(email_outbox_message.id)

        # Verify the correct number of API calls.
        self.assertEqual(get_http_mock.call_count, len(mock_api_calls), "Number of API call was %d but should be %d." %
                         (get_http_mock.call_count, len(mock_api_calls)))

        # Verify that the number of emails per label is updated with the send email message.
        label_data_after = self.verify_label_data_default.copy()
        label_data_after['all_mail'] = [True, 11, 7]
        label_data_after[settings.GMAIL_LABEL_SENT] = [True, 3, 0]
        self._label_test(self.email_account, label_data_after)

        # Verify that the specific email message has the correct labels.
        verify_labels = self.verify_label_availability_default.copy()
        verify_labels[settings.GMAIL_LABEL_INBOX] = False
        verify_labels[settings.GMAIL_LABEL_UNREAD] = False
        verify_labels[settings.GMAIL_LABEL_SENT] = True
        self._test_email_message(message_id, label_data=verify_labels)

        # Verify history id.
        self.email_account.refresh_from_db()
        self.assertEqual(self.email_account.history_id, 8095, "The history id of the email account was incorrect.")

        # Verify that the prepared outgoing message is removed from the database
        self.assertFalse(EmailOutboxMessage.objects.filter(id=email_outbox_message.id).exists(),
                         'The prepared outbox message should not be in the database anymore.')

    @patch.object(GmailService, '_get_http')
    def test_synchronize_labels_scheduler(self, get_http_mock):
        """
        Do a label synchronize for one email account.
        """

        pass  # An integrated test would be the similar with unit test of sync_labels.

    @patch.object(GmailService, '_get_http')
    def _test_full_synchronize(self, get_http_mock, mock_api_calls, label_data_after, authorized_before=True,
                               history_id_before=None, is_syncing_before=False, authorized_after=True,
                               history_id_after=8095, is_syncing_after=False):

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        # Make sure history_id is indeed missing and that the email account is in the right state.
        self._verify_email_account_state(email_account=self.email_account, authorized=authorized_before,
                                         history_id=history_id_before, is_syncing=is_syncing_before)

        # Calling the scheduler once, with a missing history_id for the email account, it will effectively do a full
        # initial synchronize.
        synchronize_email_account_scheduler()

        # Verify the correct number of API calls.
        self.assertEqual(get_http_mock.call_count, len(mock_api_calls), "Number of API call was %d but should be %d." %
                         (get_http_mock.call_count, len(mock_api_calls)))

        # Retrieve the updated email account.
        self.email_account.refresh_from_db()

        # Verify the existence of labels and the number (un)read emails per label and archived email.
        self._label_test(self.email_account, label_data_after)

        # Verify that the email account is in the right state after the synchronization has finished.
        self._verify_email_account_state(email_account=self.email_account, authorized=authorized_after,
                                         history_id=history_id_after, is_syncing=is_syncing_after)

    @patch.object(GmailService, '_get_http')
    def _test_incremental_synchronize(self, get_http_mock, mock_api_calls, label_data_after, authorized_before=True,
                                      history_id_before=None, is_syncing_before=False, authorized_after=True,
                                      history_id_after=8095, is_syncing_after=False):
        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_account = EmailAccount.objects.first()

        # Make sure history_id is indeed missing and that the email account is in the right state.
        self._verify_email_account_state(email_account=email_account, authorized=authorized_before,
                                         history_id=history_id_before, is_syncing=is_syncing_before)

        # Calling the scheduler once, with a missing history_id for the email account, it will effectively do a full
        # initial synchronize.
        synchronize_email_account_scheduler()
        # Calling the scheduler again after a succesfull full sync, will do trigger a history update.
        synchronize_email_account_scheduler()

        # Verify the correct number of API calls.
        self.assertEqual(get_http_mock.call_count, len(mock_api_calls), "Number of API call was %d but should be %d." %
                         (get_http_mock.call_count, len(mock_api_calls)))

        # Retrieve the updated email account.
        email_account.refresh_from_db()

        # Verify the existence of labels and the number (un)read emails per label and archived email.
        self._label_test(email_account, label_data_after)

        # Verify that the email account is in the right state after the synchronization has finished.
        self._verify_email_account_state(email_account=email_account, authorized=authorized_after,
                                         history_id=history_id_after, is_syncing=is_syncing_after)

    def _label_test(self, email_account, label_data):
        """
        Verify the existence of specific labels and the number (un)read emails per label and archived email.
        """
        for label_name, label_data in label_data.items():
            if label_name == 'all_mail':
                # Verify the number of archived email, ie. all email without the labels SPAM and TRASH.
                label_names_exclude = [settings.GMAIL_LABEL_SPAM, settings.GMAIL_LABEL_TRASH]
                labels = email_account.labels.filter(label_id__in=label_names_exclude)
                count_archived_mails = EmailMessage.objects.filter(account=email_account).exclude(
                    labels__in=labels).count()
                self.assertEqual(count_archived_mails, label_data[1],
                                 "Number of All mail-emails was %d but should be %d." %
                                 (count_archived_mails, label_data[1]))
            else:
                if label_data[0]:
                    db_count_per_label_total = 0
                    db_count_per_label_unread = 0
                    if email_account.labels.filter(label_id=label_name).exists():
                        # Mail with label_name should be present in the database, verify number of emails associated.
                        label = email_account.labels.filter(label_id=label_name)[0]
                        db_count_per_label_total = label.messages.count()
                        db_count_per_label_unread = label.messages.filter(read=False).count()
                        self.assertEqual(db_count_per_label_total, label_data[1],
                                         "Total number of messages for label %s was %d but should be %d." %
                                         (label_name, db_count_per_label_total, label_data[1]))
                        self.assertEqual(db_count_per_label_unread, label_data[2],
                                         "Number of unread messages for label %s was %d but should be %d." %
                                         (label_name, db_count_per_label_unread, label_data[2]))
                    else:
                        self.assertEqual(0, label_data[1],
                                         "Total number of messages for label %s was %d but should be %d." % (
                                         label_name, db_count_per_label_total, label_data[1]))
                        self.assertEqual(0, label_data[2],
                                         "Number of unread messages for label %s was %d but should be %d." % (
                                         label_name, db_count_per_label_unread, label_data[2]))
                else:
                    # Mail with label_name should not be present in the database.
                    exists = email_account.labels.filter(label_id=label_name).exists()
                    self.assertFalse(exists, "Label {0} shouldn't be in the database.".format(label_name))

    def _verify_email_account_state(self, email_account, authorized, history_id, is_syncing):
        """
        Verify if the email account is in the right state.
        """
        # Verify authorization.
        self.assertEqual(email_account.is_authorized, authorized,
                         "Account authorization for {0} incorrect.".format(email_account))

        # Verify history id.
        self.assertEqual(email_account.history_id, history_id, "The history id of the email account was incorrect.")

        # Verify if full synchronisation is in progress.
        self.assertEqual(email_account.is_syncing, is_syncing,
                         "Status of is_syncing for {0} incorrect.".format(email_account))

    def _test_email_message(self, message_id, label_data):
        """
        Verify if the email messages has the right labels.
        """
        message = EmailMessage.objects.filter(message_id=message_id).first()
        for label_name, label_available in label_data.items():
            exists = message.labels.filter(label_id=label_name).exists()
            self.assertEqual(exists, label_available, "Label {0} error on message {1}.".format(label_name, message_id))

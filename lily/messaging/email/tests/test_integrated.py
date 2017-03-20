from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock
from oauth2client.client import HttpAccessTokenRefreshError
from rest_framework.test import APITestCase

from lily.celery import app
from lily.messaging.email.factories import GmailAccountFactory
from lily.messaging.email.models.models import EmailAccount, EmailMessage
from lily.messaging.email.services import GmailService
from lily.messaging.email.tasks import synchronize_email_account_scheduler
from lily.tests.utils import UserBasedTest

from mock import patch


class EmailTests(UserBasedTest, APITestCase):
    """
    Class for integrated email testing.
    """

    verify_label_data_default = {
        # label: [available, total count, unread count],
        'archived': [True, 10, 6],  # Mail without trash, spam or chat.
        settings.GMAIL_LABEL_INBOX: [True, 5, 4],
        settings.GMAIL_LABEL_UNREAD: [True, 6, 6],
        settings.GMAIL_LABEL_STAR: [True, 1, 1],
        settings.GMAIL_LABEL_IMPORTANT: [True, 7, 6],
        settings.GMAIL_LABEL_SENT: [True, 2, 0],
        settings.GMAIL_LABEL_DRAFT: [True, 1, 0],
        settings.GMAIL_LABEL_SPAM: [True, 0, 0],
        settings.GMAIL_LABEL_TRASH: [True, 0, 0],
        settings.GMAIL_LABEL_CHAT: [True, 0, 0],
        'Label_1': [True, 3, 2],
        'Label_2': [True, 2, 2],
    }

    def setUp(self):

        def send_task(name, args=(), kwargs={}, **opts):
            # https://github.com/celery/celery/issues/581
            task = app.tasks[name]
            return task.apply(args, kwargs, **opts)

        # Let Celery execute the tasks immediately.
        app.send_task = send_task
        app.conf.update(CELERY_ALWAYS_EAGER=True)

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
        super(EmailTests, cls).setUpTestData()

        # Create an email account for the user.
        GmailAccountFactory.create(owner_id=cls.user_obj.id, tenant_id=cls.user_obj.tenant_id)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    def test_full_synchronize_single_page_history(self):
        """
        Do a full synchronize of one email account, without simulated backend errors. The history spans one API call.

        API calls to Google are mocked.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = [
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
            # Retrieve single message for getting the history_id.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            # Retrieve all 10 email messages and their labels.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_IMPORTANT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_CATEGORY_PERSONAL.json', {'status': '200'}),
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
            # Retrieve a list of all available labels.
            HttpMock('lily/messaging/email/tests/data/get_label_list.json', {'status': '200'}),
        ]

        self._test_full_synchronize(mock_api_calls=mock_api_calls, label_data_after=self.verify_label_data_default)

    def test_full_synchronize_paged_history(self):
        """
        Do a full synchronize of one email account, without simulated backend errors. The history spans more than one
        API call.

        API calls to Google are mocked.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = [
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_paged_1.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_paged_2.json', {'status': '200'}),
            # Retrieve single message for getting the history_id.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            # Retrieve all 10 email messages and their labels.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_IMPORTANT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_CATEGORY_PERSONAL.json', {'status': '200'}),
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
            # Retrieve a list of all available labels.
            HttpMock('lily/messaging/email/tests/data/get_label_list.json', {'status': '200'}),
        ]

        self._test_full_synchronize(mock_api_calls=mock_api_calls, label_data_after=self.verify_label_data_default)

    def test_full_synchronize_rate_limit_exceeded_once(self):
        """
        Do a full synchronize of one email account, with a single simulated rateLimitExceeded error.

        API calls to Google are mocked.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = [
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
            # Retrieve single message for getting the history_id.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            # Retrieve all 10 email messages and their labels.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_IMPORTANT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_CATEGORY_PERSONAL.json', {'status': '200'}),
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
            # Retrieve a list of all available labels.
            HttpMock('lily/messaging/email/tests/data/get_label_list.json', {'status': '200'}),
        ]

        self._test_full_synchronize(mock_api_calls=mock_api_calls, label_data_after=self.verify_label_data_default)

    def test_full_synchronize_failed_service_call_exception(self):
        """
        Do a full synchronize of one email account, with six simulated rateLimitExceeded errors which result in a
        FailedServiceCallException.

        API calls to Google are mocked.

        Verifies that the correct (number of) labels and related emails are stored in the database and that the
        history id and synchronisation status are administered correctly.
        """

        mock_api_calls = [
            # Retrieve a list of all the messages in the email box.
            HttpMock('lily/messaging/email/tests/data/all_message_id_list_single_page.json', {'status': '200'}),
            # Retrieve single message for getting the history_id.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            # Retrieve all 10 email messages and their labels.
            HttpMock('lily/messaging/email/tests/data/get_message_info_15a6008a4baa65f3.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_UNREAD.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_IMPORTANT.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_CATEGORY_PERSONAL.json', {'status': '200'}),
            HttpMock('lily/messaging/email/tests/data/get_label_info_INBOX.json', {'status': '200'}),
            # Simulate one FailedServiceCallException by getting six times a rateLimitExceeded error.
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            HttpMock('lily/messaging/email/tests/data/403.json', {'status': '403'}),
            # And continue with syncing after the FailedServiceCallException.
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
            # Retrieve a list of all available labels.
            HttpMock('lily/messaging/email/tests/data/get_label_list.json', {'status': '200'}),
        ]

        self._test_full_synchronize(mock_api_calls=mock_api_calls, label_data_after=self.verify_label_data_default)

    @patch.object(GmailService, 'execute_service')
    def test_full_synchronize_http_access_token_refresh_error(self, execute_service_mock):
        """
        Do a full synchronize of one email account, with a simulated HttpAccessTokenRefreshError error.

        API calls to Google are mocked.

        Verifies that the email account is unauthorized and that there are no labels and emails stored in the database.
        """

        # Mock the service execute call with a HttpAccessTokenRefreshError.
        execute_service_mock.side_effect = HttpAccessTokenRefreshError()

        email_account = EmailAccount.objects.first()

        # Calling the scheduler once, with a missing history_id for the email account, it will effectively do a full
        # initial synchronize.
        # So make sure history_id is indeed missing and that the email account is in the right state.
        self._verify_email_account_state(email_account=email_account, authorized=True, history_id=None,
                                         full_sync_finished=False)

        synchronize_email_account_scheduler()

        # Retrieve the updated email account.
        email_account.refresh_from_db()

        # Verify the existence of labels and the number (un)read emails per label and archived email.
        verify_label_data = {
            # label: [available, total count, unread count],
            'archived': [False, 0, 0],  # Mail without trash, spam or chat.
            settings.GMAIL_LABEL_INBOX: [False, 0, 0],
            settings.GMAIL_LABEL_UNREAD: [False, 0, 0],
            settings.GMAIL_LABEL_STAR: [False, 0, 0],
            settings.GMAIL_LABEL_IMPORTANT: [False, 0, 0],
            settings.GMAIL_LABEL_SENT: [False, 0, 0],
            settings.GMAIL_LABEL_DRAFT: [False, 0, 0],
            settings.GMAIL_LABEL_SPAM: [False, 0, 0],
            settings.GMAIL_LABEL_TRASH: [False, 0, 0],
            settings.GMAIL_LABEL_CHAT: [False, 0, 0],
            'Label_1': [False, 3, 2],
            'Label_2': [False, 2, 2],
        }
        self._label_test(email_account, verify_label_data)

        self._verify_email_account_state(email_account=email_account, authorized=False, history_id=None,
                                         full_sync_finished=False)

    @patch.object(GmailService, '_get_http')
    def _test_full_synchronize(self, get_http_mock, mock_api_calls, label_data_after, authorized_before=True,
                               history_id_before=None, full_sync_finished_before=False, authorized_after=True,
                               history_id_after=5948, full_sync_finished_after=True):

        # Mock the http instance with succesive http mock objects.
        get_http_mock.side_effect = mock_api_calls

        email_account = EmailAccount.objects.first()

        # Make sure history_id is indeed missing and that the email account is in the right state.
        self._verify_email_account_state(email_account=email_account, authorized=authorized_before,
                                         history_id=history_id_before, full_sync_finished=full_sync_finished_before)

        # Calling the scheduler once, with a missing history_id for the email account, it will effectively do a full
        # initial synchronize.
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
                                         history_id=history_id_after, full_sync_finished=full_sync_finished_after)

    def _label_test(self, email_account, label_data):
        """
        Verify the existence of specific labels and the number (un)read emails per label and archived email.
        """
        for label_name, label_data in label_data.items():
            if label_name == 'archived':
                # Verify the number of archived email, ie. all email without the labels SPAM, TRASH and CHAT.
                label_names_exclude = [settings.GMAIL_LABEL_SPAM, settings.GMAIL_LABEL_TRASH,
                                       settings.GMAIL_LABEL_CHAT]
                labels = email_account.labels.filter(label_id__in=label_names_exclude)
                count_archived_mails = EmailMessage.objects.filter(account=email_account).exclude(
                    labels__in=labels).count()
                self.assertEqual(count_archived_mails, label_data[1],
                                 "Archived number of emails was %d but should be %d." %
                                 (count_archived_mails, label_data[1]))
            else:
                if label_data[0]:
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
                    # Mail with label_name should not be present in the database.
                    exists = email_account.labels.filter(label_id=label_name).exists()
                    self.assertEqual(exists, False, "Label %s shouldn't be in the database." % label_name)

    def _verify_email_account_state(self, email_account, authorized, history_id, full_sync_finished):
        """
        Verify if the email account is in the right state.
        """
        # Verify authorization.
        self.assertEqual(email_account.is_authorized, authorized,
                         "Account authorization for %s incorrect." % email_account)

        # Verify history id.
        self.assertEqual(email_account.history_id, history_id, "The history id for %s was incorrect.")

        # Verify the status of the full synchronisation finished.
        self.assertEqual(email_account.full_sync_finished, full_sync_finished,
                         "Status of the full synchronisation for %s incorrect." % email_account)

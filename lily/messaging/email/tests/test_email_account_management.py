import json
from base64 import b64encode

from django.urls import reverse
from django.test import RequestFactory
from googleapiclient.discovery import build
from googleapiclient.http import HttpMock
from oauth2client.client import OAuth2WebServerFlow
from rest_framework.test import APITestCase
from rest_framework import status

from lily.messaging.email.factories import EmailAccountFactory
from lily.messaging.email.models.models import EmailAccount, SharedEmailConfig
from lily.messaging.email.services import GmailService
from lily.messaging.email.views import SetupEmailAuth, OAuth2Callback
from lily.tests.utils import UserBasedTest, get_dummy_credentials

from mock import patch


class SetupEmailAuthViewTests(UserBasedTest, APITestCase):
    """
    Class for unit testing email account management, particular the first step of the oauth-flow where the user leaves
    Lily for Google to choose an email account to add.
    """

    def setUp(self):
        self.factory = RequestFactory()

    @patch.object(OAuth2WebServerFlow, 'step1_get_authorize_url')
    def test_get(self, step1_get_authorize_url_mock):
        """
        Test the email setup view on doing the first call to the OAUTH flow and redirecting to the right follow up url.
        """
        step1_get_authorize_url_mock.return_value = ''

        # Make a request to the email setup view.
        request = self.factory.get(reverse('messaging_email_account_setup'))
        request.user = self.user_obj
        response = SetupEmailAuth.as_view()(request)

        # Verify it is redirecting and to the right url.
        self.assertEqual(response.status_code, 302)
        step1_get_authorize_url_mock.assert_called_once()
        self.assertEqual(response.url, step1_get_authorize_url_mock.return_value)


class OAuth2CallbackViewTests(UserBasedTest, APITestCase):
    """
    Class for unit testing email account management, particular the second step of the oauth-flow where Google
    redirects back to Lily with an authorization token for the choosen email account.
    """

    def setUp(self):
        self.factory = RequestFactory()

        # Patch the creation of a Gmail API service without the need for authorized credentials.
        self.credentials = get_dummy_credentials()
        self.get_credentials_mock_patcher = patch('lily.messaging.email.connector.get_credentials')
        get_credentials_mock = self.get_credentials_mock_patcher.start()
        get_credentials_mock.return_value = self.credentials

        self.authorize_mock_patcher = patch.object(GmailService, 'authorize')
        authorize_mock = self.authorize_mock_patcher.start()
        authorize_mock.return_value = None

        self.build_service_mock_patcher = patch.object(GmailService, 'build_service')
        build_service_mock = self.build_service_mock_patcher.start()
        build_service_mock.return_value = build('gmail', 'v1', credentials=self.credentials)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    @patch.object(GmailService, '_get_http')
    @patch.object(OAuth2WebServerFlow, 'step2_exchange')
    @patch('lily.messaging.email.views.validate_token')
    def test_get(self, validate_token_mock, step2_exchange_mock, get_http_mock):
        """
        Test the creation of an email account after authorization via Google.
        """
        state = b64encode('{"token": "123"}')
        code = '456'

        validate_token_mock.return_value = True
        step2_exchange_mock.return_value = self.credentials
        get_http_mock.return_value = HttpMock('lily/messaging/email/tests/data/profile.json', {'status': '200'})

        # Make a request to the oauth-callback view.
        request = self.factory.get('{0}?state={1}&code={2}'.format(reverse('gmail_callback'), state, code))
        request.user = self.user_obj
        response = OAuth2Callback.as_view()(request)

        # A valid authorization token was mocked, so verify that the user is redirected to the email setup screen.
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url,
                         '/#/preferences/emailaccounts/setup/{0}'.format(EmailAccount.objects.latest('id').pk))

        # Verify that an email account was added to the database belonging to the user.
        email_account = EmailAccount.objects.get(email_address='firstname.lastname@example.com')
        self.assertEqual(email_account.owner, self.user_obj)
        self.assertFalse(email_account.is_deleted)
        self.assertFalse(email_account.is_authorized)  # An newly added email account isn't authorized yet.
        self.assertIsNone(email_account.history_id)

    def test_get_invalid_token(self):
        """
        Test the proper handling of an invalid authorization token.
        """
        state = b64encode('{"token": "123"}')  # Invalid authorization token.

        # Make a request to the oauth-callback view.
        request = self.factory.get('{0}?state={1}'.format(reverse('gmail_callback'), state))
        request.user = self.user_obj
        response = OAuth2Callback.as_view()(request)

        # Verify that with the provided invalid token the response is a bad request.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('lily.messaging.email.views.messages.error')
    def test_add_email_account_deny_authorization(self, messages_error_mock):
        """
        Test when the user denies the oauth authorization step.
        """
        # Mock the messages, because the MessageMiddleware isn't available during tests.
        messages_error_mock.return_value = True

        state = b64encode('{"token": "123"}')
        error = "access_denied"

        # Make a request to the oauth-callback view.
        request = self.factory.get('{0}?error={1}&state={2}'.format(reverse('gmail_callback'), error, state))
        request.user = self.user_obj
        response = OAuth2Callback.as_view()(request)

        # Verify that the error leads to a redirect back to the email accounts page and
        # that a notification message was added.
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '/#/preferences/emailaccounts')
        messages_error_mock.assert_called_once()


class EmailAccountManagementTests(UserBasedTest, APITestCase):
    """
    Class for unit testing email account management.
    """

    def setUp(self):
        self.factory = RequestFactory()

        # Patch the creation of a Gmail API service without the need for authorized credentials.
        self.credentials = get_dummy_credentials()
        self.get_credentials_mock_patcher = patch('lily.messaging.email.api.serializers.get_credentials')
        get_credentials_mock = self.get_credentials_mock_patcher.start()
        get_credentials_mock.return_value = self.credentials

        self.authorize_mock_patcher = patch.object(GmailService, 'authorize')
        authorize_mock = self.authorize_mock_patcher.start()
        authorize_mock.return_value = None

        self.build_service_mock_patcher = patch.object(GmailService, 'build_service')
        build_service_mock = self.build_service_mock_patcher.start()
        build_service_mock.return_value = build('gmail', 'v1', credentials=self.credentials)

    @classmethod
    def setUpTestData(cls):
        # Create a user, handled by UserBasedTest.
        super(EmailAccountManagementTests, cls).setUpTestData()

        # Create an email account for the user.
        cls.email_accounts = EmailAccountFactory.create_batch(size=2, owner=cls.user_obj, tenant=cls.user_obj.tenant,
                                                              is_authorized=False)

    def tearDown(self):
        self.get_credentials_mock_patcher.stop()
        self.authorize_mock_patcher.stop()
        self.build_service_mock_patcher.stop()

    def test_add_email_account_full_sync(self):
        """
        After adding an email account via OAUTH the user has to do some settings for the account.

        Test by editting the account to synchronize all the email messages.
        """
        # Setup the data to patch the email account with.
        email_account = self.email_accounts[0]
        from_name = "Firstname Lastname"
        label = "ABC"
        only_new = False
        privacy = EmailAccount.READ_ONLY
        shared_email_configs = []
        stub_dict = {'id': email_account.pk, 'from_name': from_name, 'label': label, 'only_new': only_new,
                     'privacy': privacy, 'shared_email_configs': shared_email_configs}

        # Make the API call to patch the email account.
        response = self.user.patch('/api/messaging/email/accounts/{0}/'.format(email_account.pk),
                                   data=stub_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the email account is up to date with the patched data.
        email_account.refresh_from_db()
        self.assertTrue(email_account.is_authorized)
        self.assertIsNone(email_account.history_id)  # Because only_new=False the history id isn't set.
        self.assertEqual(email_account.from_name, from_name)
        self.assertEqual(email_account.label, label)
        self.assertEqual(email_account.privacy, EmailAccount.READ_ONLY)

    @patch.object(GmailService, '_get_http')
    def test_add_email_account_sync_now(self, get_http_mock):
        """
        After adding an email account via OAUTH the user has to do some settings for the account.

        Test by editting the account to synchronize only the email messages from this moment on.
        """
        # The google profile is retrieved to get the current history id, mock that API call.
        get_http_mock.return_value = HttpMock('lily/messaging/email/tests/data/profile.json', {'status': '200'})

        # Setup the data to patch the email account with.
        email_account = self.email_accounts[0]
        from_name = "Firstname Lastname"
        label = "ABC"
        only_new = True
        privacy = EmailAccount.READ_ONLY
        shared_email_configs = []
        stub_dict = {'id': email_account.pk, 'from_name': from_name, 'label': label, 'only_new': only_new,
                     'privacy': privacy, 'shared_email_configs': shared_email_configs}

        # Make the API call to patch the email account.
        response = self.user.patch('/api/messaging/email/accounts/{0}/'.format(email_account.pk),
                                   data=stub_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the email account is up to date with the patched data.
        email_account.refresh_from_db()
        self.assertTrue(email_account.is_authorized)
        self.assertEqual(email_account.history_id, 557200)
        self.assertEqual(email_account.from_name, from_name)
        self.assertEqual(email_account.label, label)
        self.assertEqual(email_account.privacy, EmailAccount.READ_ONLY)

    def test_private_sharing(self):
        """
        Test setting an email account privacy to private, but share it with one colleague.
        """
        # Setup the data to patch the email account with.
        email_account = self.email_accounts[0]
        from_name = "Firstname Lastname"
        label = "ABC"
        only_new = False
        privacy = EmailAccount.PRIVATE
        # Share one of my email account with another user.
        shared_email_configs = [{"user": self.superuser_obj.pk, "privacy": EmailAccount.PUBLIC,
                                 "email_account": self.email_accounts[0].pk}]
        # TODO: Sharing with a user of an other tenant is possible via tests, should be restricted by tenant.
        # But it is restricted in the frontend.

        stub_dict = {'id': email_account.pk, 'from_name': from_name, 'label': label, 'only_new': only_new,
                     'privacy': privacy, 'shared_email_configs': shared_email_configs}

        # Make the API call to patch the email account.
        response = self.user.patch('/api/messaging/email/accounts/{0}/'.format(email_account.pk),
                                   data=stub_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the email account is up to date with the patched data.
        email_account.refresh_from_db()
        self.assertEqual(email_account.privacy, EmailAccount.PRIVATE)
        sec = SharedEmailConfig.objects.filter(email_account=self.email_accounts[0].pk)[0]
        self.assertEqual(sec.user, self.superuser_obj)
        self.assertEqual(sec.privacy, EmailAccount.PUBLIC)

    def test_private_revert_sharing(self):
        """
        Test revert sharing an private email account with a colleague.
        """
        # Setup the data to patch the email account with.
        email_account = self.email_accounts[0]
        from_name = "Firstname Lastname"
        label = "ABC"
        only_new = False
        privacy = EmailAccount.PRIVATE

        # Share one of my email accounts with another user.
        shared_email_configs = [{"user": self.superuser_obj.pk, "privacy": EmailAccount.PUBLIC,
                                 "email_account": self.email_accounts[0].pk}]

        stub_dict = {'id': email_account.pk, 'from_name': from_name, 'label': label, 'only_new': only_new,
                     'privacy': privacy, 'shared_email_configs': shared_email_configs}

        # Make the API call to patch the email account.
        response = self.user.patch('/api/messaging/email/accounts/{0}/'.format(email_account.pk),
                                   data=stub_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(SharedEmailConfig.objects.filter(email_account=self.email_accounts[0]).exists())

        # Revert sharing one of my email accounts with another user.
        shared_email_configs[0]['id'] = SharedEmailConfig.objects.latest('id').pk
        shared_email_configs[0]['is_deleted'] = True
        stub_dict['shared_email_configs'] = shared_email_configs

        # Make the API call to patch the email account.
        response = self.user.patch('/api/messaging/email/accounts/{0}/'.format(email_account.pk),
                                   data=stub_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that the previous created shared email config object is not available anymore.
        self.assertFalse(SharedEmailConfig.objects.filter(email_account=self.email_accounts[0]).exists())

    def test_delete_email_account(self):
        """
        Test soft deleting an email account.
        """
        email_account = self.email_accounts[0]
        response = self.user.delete('/api/messaging/email/accounts/{0}/'.format(email_account.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(EmailAccount.objects.get(pk=email_account.pk).is_deleted)

    def test_set_primary_email_account(self):
        """
        Test toggling the primary email account.
        """
        # Verify that initially no primary email account is set for the user.
        self.assertIsNone(self.user_obj.primary_email_account)

        # Api call to set primary email account.
        request = self.user.patch('/api/users/me/',
                                  {'id': 'me', 'primary_email_account': {'id': self.email_accounts[0].pk}},
                                  format='json')

        # Verify the request was succesfull and the user account has the right primary email account set.
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.user_obj.refresh_from_db()
        primary_email_account_id = json.loads(request.content).get('primary_email_account').get('id')
        self.assertEqual(self.user_obj.primary_email_account.pk, primary_email_account_id)

        # Switch to another email account as the primary one.
        response = self.user.patch('/api/users/me/',
                                   {'id': 'me', 'primary_email_account': {'id': self.email_accounts[1].pk}},
                                   format='json')

        # Verify the request was succesfull and the user account has the right primary email account set.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_obj.refresh_from_db()
        primary_email_account_id = json.loads(response.content).get('primary_email_account').get('id')
        self.assertEqual(self.user_obj.primary_email_account.pk, primary_email_account_id)

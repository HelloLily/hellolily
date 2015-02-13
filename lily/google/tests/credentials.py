from threading import local
from urllib import urlencode
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from oauth2client import xsrfutil
from oauth2client.client import FlowExchangeError

from lily.google.credentials import get_credentials, get_credentials_link
from lily.tenant.factories import TenantFactory
from lily.users.factories import LilyUserFactory
from lily.tenant.middleware import get_current_user

_thread_locals = local()


@override_settings(STATICFILES_STORAGE='pipeline.storage.NonPackagingPipelineStorage', PIPELINE_ENABLED=False)
class CredentialsTestCase(TestCase):
    def setUp(self):
        self.callback_url = reverse('google_oauth2callback')

    def _get_logged_in_user(self):
        tenant = TenantFactory()
        current_user = get_current_user()
        # Ugly!
        if current_user:
            current_user.tenant = tenant
        user = LilyUserFactory(tenant=tenant)
        user.set_password('test')
        user.save()
        self.client.login(username=user.primary_email.email_address, password='test')
        return user

    def _get_validation_token(self, user):
        return xsrfutil.generate_token(settings.SECRET_KEY, user)

    def _check_validation_token(self, user, token):
        return xsrfutil.validate_token(settings.SECRET_KEY, token, user)

    def test_new_user_has_invalid_credentials(self):

        user = LilyUserFactory.build()
        self.assertIsNone(get_credentials(user))

    def test_new_user_can_create_credentials(self):
        user = self._get_logged_in_user()

        url = get_credentials_link(user)
        self.assertIsInstance(url, basestring)
        self.assertIn('https://', url)
        self.assertIn(urllib.quote(reverse('google_oauth2callback'), safe=''), url)
        self.assertIn('state=%s' % self._get_validation_token(user), url)

    def test_credential_link_has_state(self):
        user = self._get_logged_in_user()
        token = xsrfutil.generate_token(settings.SECRET_KEY, user)
        url = get_credentials_link(user)

        self.assertIn(token, url)

    def test_callback_url_needs_login(self):
        resp = self.client.get(self.callback_url)
        login_url = '%s?next=%s' % (reverse('login'), self.callback_url)
        self.assertRedirects(resp, login_url)

    def test_callback_url_checks_invalid_request(self):
        self._get_logged_in_user()
        resp = self.client.get(self.callback_url)
        self.assertEqual(resp.status_code, 400)

        query_dict = {
            'state': 'fake_code',
        }

        url = '%s?%s' % (self.callback_url, urlencode(query_dict))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 400)

    def test_callback_url_checks_invalid_query_request(self):
        user = self._get_logged_in_user()
        query_dict = {
            'state': self._get_validation_token(user),
            'code': 'invalid code'
        }

        url = '%s?%s' % (self.callback_url, urlencode(query_dict))
        with(self.assertRaises(FlowExchangeError)):
            self.client.get(url)

    def tearDown(self):
        pass

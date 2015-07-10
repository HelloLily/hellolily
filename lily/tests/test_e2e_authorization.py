from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.test import override_settings
from protractor.test import ProtractorTestCaseMixin

from lily.users.factories import LilyUserFactory


class AuthorizationTestCase(ProtractorTestCaseMixin, StaticLiveServerTestCase):
    specs = ['tests/e2e/authorization-spec.js']
    live_server_url = settings.TEST_SITE_URL

    def setUp(self):
        """
        Setup fixtures before running e2e test.
        """
        super(AuthorizationTestCase, self).setUp()
        call_command('index')
        LilyUserFactory.create(is_active=True, email='user1@lily.com', password=make_password('testing'))

    @override_settings(DEBUG=True)
    def test_run(self):
        super(AuthorizationTestCase, self).test_run()

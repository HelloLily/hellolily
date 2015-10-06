from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from protractor.test import ProtractorTestCaseMixin

from lily.users.factories import LilyUserFactory


class AuthorizationTestCase(ProtractorTestCaseMixin, StaticLiveServerTestCase):
    specs = ['tests/e2e/authorization-spec.js']

    def setUp(self):
        """
        Setup fixtures before running e2e test.
        """
        super(AuthorizationTestCase, self).setUp()
        call_command('index')
        call_command('testdata', target='contacts_and_accounts,cases,deals,notes')
        LilyUserFactory.create(is_active=True, email='user1@lily.com', password=make_password('testing'))

    def test_run(self):
        super(AuthorizationTestCase, self).test_run()

    def tearDown(self):
        # Workaround for https://code.djangoproject.com/ticket/10827
        ContentType.objects.clear_cache()

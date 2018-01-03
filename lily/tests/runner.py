import logging

from django.test.runner import DiscoverRunner

from django.conf import settings


class LilyNoseTestSuiteRunner(DiscoverRunner):
    """
    Bootstrap into the testsuite running process.

    Customize settings to run the test suite without problems.
    Settings it changes:
        * TESTING=True, useful to check if we are running tests.
    """
    def __init__(self, *args, **kwargs):
        super(LilyNoseTestSuiteRunner, self).__init__(*args, **kwargs)

        if settings.TEST_SUPPRESS_LOG:
            # Suppress logging during a testrun.
            logging.disable(logging.CRITICAL)

        settings.TESTING = True

        # manage.py test already does this, but not when providing a path, like
        # manage.py test lily/contacts/tests.
        settings.DEBUG = False

import logging

from django.test.runner import DiscoverRunner

from django.conf import settings


class LilyNoseTestSuiteRunner(object):
    """
    Bootstrap into the testsuite running process.

    Customize settings to run the test suite without problems.
    Settings it changes:
        * TESTING=True, useful to check if we are running tests.
    """
    def __init__(self, verbosity=1, failfast=False, keepdb=False, *args, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb

        if settings.TEST_SUPPRESS_LOG:
            # Suppress logging during a testrun.
            logging.disable(logging.CRITICAL)

        settings.TESTING = True

        # manage.py test already does this, but not when providing a path, like
        # manage.py test lily/contacts/tests.
        settings.DEBUG = False

    def run_tests(self, test_labels):
        """Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """
        import pytest

        argv = []
        if self.verbosity == 0:
            argv.append('--quiet')
        if self.verbosity == 2:
            argv.append('--verbose')
        if self.verbosity == 3:
            argv.append('-vv')
        if self.failfast:
            argv.append('--exitfirst')
        if self.keepdb:
            argv.append('--reuse-db')

        argv.extend(test_labels)
        return pytest.main(argv)

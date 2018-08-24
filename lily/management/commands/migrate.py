import os
import traceback

from django.conf import settings
from django.core.management.commands import migrate

from slacker import Slacker


class Command(migrate.Command):
    def handle(self, *args, **options):
        """
        Wrapper around default django migrate command to print a default message and send a slack message on error.
        """
        settings.MIGRATING = True

        try:
            super(Command, self).handle(*args, **options)
        except Exception, e:
            traceback.print_exc()
            self.stderr.write('\nMigration error.\n')

            heroku_env = os.environ.get('HEROKU_ENV')
            if heroku_env == 'production':
                travis_build = os.environ.get('TRAVIS_BUILD_ID')
                travis_link = 'https://travis-ci.org/HelloLily/hellolily/builds/{0}'.format(travis_build)
                slack = Slacker(os.environ.get('SLACK_API_TOKEN'))
                slack.chat.post_message(
                    '#lily_ci',
                    'Migration failed with reason `{0}` in Travis build {1}.'.format(repr(e), travis_link)
                )
        else:
            # Set migrating to False again to prevent tests failing.
            settings.MIGRATING = False

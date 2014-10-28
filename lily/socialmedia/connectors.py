import re
from urlparse import urlparse

from django.utils.translation import ugettext as _


class BaseConnector(object):
    """
    Base class for all social media connectors

    Attributes:
        _profile_base_url (string): the url used to build the profile url.
        _hostname (string): the hostname used to check if links are valid.
        _username_regex (regex string): the regex used to recognize usernames in urls.
    """
    _profile_base_url = ''
    _hostname = ''
    _username_regex = ''

    def __init__(self, url=None, username=None):
        """
        Initialize the connector class instance. Either url or username must be given.

        Args:
            url (string): the url from which the username must be parsed.
            username (string): the username used to build the profile url with.

        Raises:
            TypeError: when no url or username is passed.
            ValueError: when the username can't be guessed with certainty.
        """
        if not username and not url:
            raise TypeError('__init__() takes at least one argument, either username or url')

        self.username = username or self._get_username(url)
        self.profile_url = self._get_profile_url(username=self.username)

    def _get_username(self, string):
        """
        Parse the input for a username.

        Args:
            string (string): url or username to parse.

        Returns:
            username (string): the username which was parsed from the input.
        """
        parsed_url = urlparse(string)

        if parsed_url.hostname == self._hostname and parsed_url.path:
            regex = re.compile(self._username_regex, re.IGNORECASE)
            match = regex.match(parsed_url.path)

            if match is not None:
                return match.group('username')
        elif not parsed_url.hostname:
            return string
        raise ValueError(_('Invalid username or url'))

    def _get_profile_url(self, username):
        """
        Build a profile url.

        Args:
            username (string): the username to use in the profile url.

        Returns:
            profile_url (string): the full profile url including username.
        """
        return self._profile_base_url % {
            'username': username,
        }


class Twitter(BaseConnector):
    """
    Connector class for use with twitter accounts.
    """
    _profile_base_url = 'https://twitter.com/%(username)s'
    _hostname = 'twitter.com'
    _username_regex = '/(?P<username>[a-zA-Z0-9_]*)'


class LinkedIn(BaseConnector):
    """
    Connector class for use with linkedin accounts.
    """
    _profile_base_url = 'https://www.linkedin.com/in/%(username)s'
    _hostname = 'www.linkedin.com'
    _username_regex = '/in/(?P<username>[a-zA-Z0-9_]*)'

import re
import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _


class BaseConnector(object):
    """
    Base class for all social media connectors

    Attributes:
        _username_regex (regex string): the regex used to check validity of profile urls.
        _profile_url_regex (regex string): the regex used to check validity of usernames.
        _profile_base_url (string): the url used to generate the profile url if not provided.
    """
    _domain = ''
    _username_regex = re.compile('')
    _profile_url_base = ''
    _profile_url_paths = ()
    _profile_url_allowed_query_params = ()
    _profile_url_validator = URLValidator(schemes=['http', 'https'])

    def __init__(self, username=None, profile_url=None):
        """
        Initialize the connector class instance. Either username or profile_url must be given.

        Args:
            username (string): the username used to build the profile url with.
            profile_url (string): the url from which the username must be parsed.

        Raises:
            TypeError: when no username or profile_url is passed.
            ValidationError: when the username or profile_url is not valid.
        """
        if username and profile_url:
            self._parse_username(username)
            self._parse_profile_url(profile_url)
        elif username:
            self._parse_username(username, autofill=True)
        elif profile_url:
            self._parse_profile_url(profile_url, autofill=True)
        else:
            raise TypeError('__init__() takes at least one argument, username and/or profile_url')

    def _parse_username(self, username, autofill=False):
        """
        Parse the username for validity.

        Args:
            username (string): the username to parse, could be a profile url.
            autofill (boolean): whether or not to autofill the profile url based on username.

        Raises:
            ValidationError: When the username is not valid.
        """

        # We want clean usernames in the database, so strip certain characters.
        username = username.replace('@', '')

        if self._username_regex.match(username):
            if autofill:
                self.profile_url = self._profile_url_base % {'username': username}

            self.username = username
        else:
            try:
                # We didn't receive a normal username so try if it's a profile url instead.
                self._parse_profile_url(username, autofill=True)
            except ValidationError:
                raise ValidationError(_('Invalid username, incorrect format.'))

    def _parse_profile_url(self, profile_url, autofill=False):
        """
        Parse the profile url for validity.

        Args:
            profile_url (string): the profile url to parse.
            autofill (boolean): whether or not to autofill the username based on profile url.

        Raises:
            ValidationError: When the profile url is not valid.
        """
        # Try to fix url scheme before validation.
        profile_url = 'https://' + profile_url if not profile_url.startswith('http') else profile_url

        # Validate the url, not social media specific.
        try:
            self._profile_url_validator(profile_url)
        except ValidationError:
            raise ValidationError(_('Invalid profile url, not a valid url.'))

        # The url is valid, so determine if it's a valid social media profile url.
        parse_result = urlparse.urlparse(profile_url)

        if not parse_result.netloc.endswith(self._domain):
            raise ValidationError(_('Invalid profile url, linking to wrong website.'))

        # Build the path string to match against
        path_string = parse_result.path

        if self._profile_url_allowed_query_params:
            # Filter the query params, we don't need unnecessary crap.
            query_string = ''
            for query_key, query_value in urlparse.parse_qs(parse_result.query).items():
                if query_key in self._profile_url_allowed_query_params:
                    query_string += '&%s=%s' % (query_key, query_value[0])
            # Strip the leading '&' if necessary
            query_string = query_string[1:] if query_string else ''

            if query_string:
                path_string = parse_result.path + '?' + query_string

        # We are linking to the correct website.
        for path in self._profile_url_paths:
            match = path.match(path_string)

            if match:
                # The path is valid for this social media.
                if autofill:
                    self.username = match.group('username')
                break
        else:
            # We didn't break so we didn't find a valid path throw error.
            raise ValidationError(_('Invalid profile url, username or id could not be parsed.'))

        self.profile_url = '%s://%s%s' % (parse_result.scheme, parse_result.netloc, path_string)


class Twitter(BaseConnector):
    """
    Connector class for use with twitter accounts.
    """
    _domain = 'twitter.com'
    _username_regex = re.compile(r'[a-z0-9._-]+$', re.IGNORECASE)
    _profile_url_base = 'https://twitter.com/%(username)s'
    _profile_url_paths = (re.compile(r'/(?P<username>[a-z0-9._-]+)/?$', re.IGNORECASE), )
    _profile_url_allowed_query_params = ()


class LinkedIn(BaseConnector):
    """
    Connector class for use with linkedin accounts.
    """
    _domain = 'linkedin.com'
    _username_regex = re.compile('[a-z0-9._-]+$', re.IGNORECASE)
    _profile_url_base = 'https://www.linkedin.com/in/%(username)s'
    _profile_url_paths = (
        re.compile(r'/in/(?P<username>[a-z0-9._-]*)/?$', re.IGNORECASE),
        re.compile(r'/profile/view\?*.(id=(?P<username>\w{39}))/?', re.IGNORECASE),
    )
    _profile_url_allowed_query_params = ('id', )

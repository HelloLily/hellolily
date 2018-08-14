from urlparse import urlparse

from django.conf import settings
from django.contrib.sites.models import Site


def mail_to_lily(attrs, new=False):
    """
    Convert mailto links to use lily mail instead of default mailto app.
    """
    if attrs['href'].startswith('mailto:'):
        protocol = 'http' if settings.DEBUG else 'https'

        # Get the current site or empty string.
        try:
            # Django caches the site object, so no worries about a query for every a tag.
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = ''

        # For now we only support one email address pre-filled in the compose.
        recipient = urlparse(attrs['href']).path.split(',').pop()

        attrs['href'] = '%s://%s/#/email/compose/%s' % (protocol, current_site, recipient)

    return attrs


# TODO: this was removed, but server side nothing is sanitized anymore.
# TODO: restore this to how it was so the api is safe again.
class HtmlSanitizer(object):
    """
    Interface class for bleach. Making it easier to work with by setting project defaults.
    """

    def __init__(self, html):
        self.html = html

    def clean(self):
        # Probably not needed anymore since the Markdown lib sanitizes the HTML.
        # self.html = cgi.escape(self.html)

        return self

    def render(self):
        return self.html

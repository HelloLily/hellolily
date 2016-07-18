from urlparse import urlparse

import bleach
from django.conf import settings
from django.contrib.sites.models import Site
from html5lib.sanitizer import HTMLSanitizerMixin


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


class BlackList(object):
    """
    This class reverses the *in* lookup of python iterables, effectively converting it into a *not in*.
    """
    def __init__(self, iterable):
        self.iterable = iterable

    def __contains__(self, value):
        return value not in self.iterable


class HtmlSanitizer(object):
    """
    Interface class for bleach. Making it easier to work with by setting project defaults.
    """
    STRICT_TAG_LIST = bleach.ALLOWED_TAGS
    STRICT_ATTR_LIST = bleach.ALLOWED_ATTRIBUTES
    STRICT_STYLE_LIST = bleach.ALLOWED_STYLES

    LENIENT_TAG_LIST = HTMLSanitizerMixin.allowed_elements + [
        'base', 'bdi', 'body', 'data', 'head', 'html', 'link', 'main', 'mark', 'menuitem', 'meta', 'rp', 'rt', 'ruby',
        'style', 'summary', 'title', 'wbr'
    ]
    LENIENT_ATTR_LIST = HTMLSanitizerMixin.allowed_attributes + [
        'autosave', 'cid', 'dropzone', 'novalidate', 'placeholder', 'pubdate', 'reversed', 'spellcheck'
    ]
    LENIENT_STYLE_LIST = HTMLSanitizerMixin.allowed_css_properties + [
        'background', 'background-attachment', 'background-image', 'background-position', 'background-repeat',
        'border', 'border-bottom', 'border-bottom-style', 'border-bottom-width', 'border-left', 'border-left-style',
        'border-left-width', 'border-right', 'border-right-style', 'border-right-width', 'border-spacing',
        'border-style', 'border-top', 'border-top-style', 'border-top-width', 'border-width', 'bottom', 'caption-side',
        'clip', 'content', 'counter-increment', 'counter-reset', 'empty-cells', 'left', 'list-style',
        'list-style-image', 'list-style-position', 'list-style-type', 'margin', 'margin-bottom', 'margin-left',
        'margin-right', 'margin-top', 'max-height', 'max-width', 'min-height', 'min-width', 'opacity', 'orphans',
        'outline', 'outline-color', 'outline-style', 'outline-width', 'padding', 'padding-bottom', 'padding-left',
        'padding-right', 'padding-top', 'page-break-after', 'page-break-before', 'page-break-inside', 'quotes',
        'right', 'table-layout', 'text-transform', 'top', 'url', 'visibility', 'widows', 'word-spacing', 'z-index'
    ]

    DEFAULT_CALLBACKS = bleach.DEFAULT_CALLBACKS + [mail_to_lily, ]

    def __init__(self, html):
        self.html = html

    def clean(self, tag_list=STRICT_TAG_LIST, attr_list=STRICT_ATTR_LIST, style_list=STRICT_STYLE_LIST,
              blacklist=False, strip=False, strip_comments=True):
        if blacklist:
            # Wrap lists in BlackList class, for reversal of the matching.
            tag_list = BlackList(tag_list)
            attr_list = BlackList(attr_list)
            style_list = BlackList(style_list)

        self.html = bleach.clean(
            self.html,
            tags=tag_list,
            attributes=attr_list,
            styles=style_list,
            strip=strip,
            strip_comments=strip_comments
        )

        return self

    def render(self):
        return self.html

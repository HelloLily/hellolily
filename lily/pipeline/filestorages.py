import urlparse

from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin
from storages.backends.s3boto import S3BotoStorage


def domain(url):
    """
    Return the domain for the given url.

    Arguments:
        url (str): the url for which to return the domain.
    """
    return urlparse.urlparse(url).hostname


class MediaFilesStorage(S3BotoStorage):
    """
    The storage classed used to upload files to the media bucket on amazon.
    """

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.MEDIA_ROOT
        kwargs['acl'] = 'private'
        kwargs['querystring_expire'] = 300
        super(MediaFilesStorage, self).__init__(*args, **kwargs)


class StaticFilesStorage(CachedFilesMixin, S3BotoStorage):
    """
    The storage class used to concatenate, minify and  upload files to the static bucket on amazon.
    """

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.STATIC_ROOT
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        kwargs['acl'] = 'private'
        super(StaticFilesStorage, self).__init__(*args, **kwargs)

    def hashed_name(self, name, content=None, filename=None):
        try:
            out = super(StaticFilesStorage, self).hashed_name(name, content, filename)
        except ValueError:
            # This means that a file could not be found, and normally this would
            # cause a fatal error, which seems rather excessive given that
            # some packages have missing files in their css all the time.
            out = name
        return out

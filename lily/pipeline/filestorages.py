import urlparse

from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin
from pipeline.storage import PipelineMixin
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
        kwargs['custom_domain'] = domain(settings.MEDIA_URL)
        super(MediaFilesStorage, self).__init__(*args, **kwargs)


class StaticFilesStorage(PipelineMixin, CachedFilesMixin, S3BotoStorage):
    """
    The storage class used to concatenate, minify and  upload files to the static bucket on amazon.
    """

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.STATIC_ROOT
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        super(StaticFilesStorage, self).__init__(*args, **kwargs)

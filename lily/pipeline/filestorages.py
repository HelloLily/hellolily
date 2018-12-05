import urlparse
from mimetypes import guess_type

from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin
from storages.backends.s3boto import S3BotoStorage
from django.utils.encoding import filepath_to_uri


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

    def generate_presigned_post_url(self, name, expire=3600):
        # Preserve the trailing slash after normalizing the path.
        name = self._normalize_name(self._clean_name(name))
        if self.custom_domain:
            return '%s//%s/%s' % (self.url_protocol, self.custom_domain, filepath_to_uri(name))

        if expire is None:
            expire = self.querystring_expire

        content_type, _ = guess_type(name)

        return self.connection.generate_url(
            expire,
            method='PUT',
            bucket=self.bucket.name,
            key=self._encode_name(name),
            headers={'Content-Type': content_type},
            query_auth=self.querystring_auth,
            force_http=not self.secure_urls,
            response_headers={},
        )


class StaticFilesStorage(CachedFilesMixin, S3BotoStorage):
    """
    The storage class used to concatenate, minify and  upload files to the static bucket on amazon.
    """

    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.STATIC_ROOT
        kwargs['custom_domain'] = domain(settings.STATIC_URL)
        # Don't think this is even used
        # Should be set with env var AWS_S3_CUSTOM_DOMAIN
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

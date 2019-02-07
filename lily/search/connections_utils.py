import urllib3

import certifi
from django.conf import settings
from elasticsearch_old.connection.http_urllib3 import Urllib3HttpConnection
from elasticsearch_old.exceptions import ImproperlyConfigured
from elasticutils.contrib.django import get_es


def get_es_client(**kwargs_overrides):
    return get_es(**get_es_client_kwargs(**kwargs_overrides))


def get_es_client_kwargs(**kwargs_overrides):
    """
    Returns the ES client configured from settings.
    """
    client_kwargs = {
        'verify_certs': True,
        'ca_certs': certifi.where(),
        'urls': settings.ES_OLD_URLS,
        'timeout': settings.ES_OLD_TIMEOUT,
        'maxsize': settings.ES_OLD_MAXSIZE,
        'retry_on_status': (503, 504, 429),  # we add 429 (for concurrent requests)
        'connection_class': Urllib3HttpBlockingConnection,
        'block': settings.ES_OLD_BLOCK
    }
    client_kwargs.update(kwargs_overrides)
    return client_kwargs


def get_index_name(base_index_name, mapping):
    """Returns the full index name, based on the base index name and mapping or type."""
    if 'get_mapping_type_name' in dir(mapping):
        return '%s.%s' % (base_index_name, mapping.get_mapping_type_name())
    return '%s.%s' % (base_index_name, mapping)


class Urllib3HttpBlockingConnection(Urllib3HttpConnection):
    """
    Default connection class using the `urllib3`, with blocking option.

    Note that the code is mostly copy paste from `Urllib3HttpConnection`.
    The only difference is the addition of the `block` kwarg.

    :arg http_auth: optional http auth information as either ':' separated
        string or a tuple
    :arg use_ssl: use ssl for the connection if `True`
    :arg verify_certs: whether to verify SSL certificates
    :arg ca_certs: optional path to CA bundle. See
        http://urllib3.readthedocs.org/en/latest/security.html#using-certifi-with-urllib3
        for instructions how to get default set
    :arg client_cert: path to the file containing the private key and the
        certificate
    :arg maxsize: the maximum number of connections which will be kept open to
        this host.
    """
    def __init__(self, host='localhost', port=9200, http_auth=None,
                 use_ssl=False, verify_certs=False, ca_certs=None, client_cert=None,
                 maxsize=10, block=False, **kwargs):

        super(Urllib3HttpConnection, self).__init__(host=host, port=port, **kwargs)
        self.headers = {}
        if http_auth is not None:
            if isinstance(http_auth, (tuple, list)):
                http_auth = ':'.join(http_auth)
            self.headers = urllib3.make_headers(basic_auth=http_auth)

        pool_class = urllib3.HTTPConnectionPool
        kw = {}
        if use_ssl:
            pool_class = urllib3.HTTPSConnectionPool

            if verify_certs:
                kw['cert_reqs'] = 'CERT_REQUIRED'
                kw['ca_certs'] = ca_certs
                kw['cert_file'] = client_cert
            elif ca_certs:
                raise ImproperlyConfigured("You cannot pass CA certificates when verify SSL is off.")

        self.pool = pool_class(host, port=port, timeout=self.timeout, maxsize=maxsize, block=block, **kw)

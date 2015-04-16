import certifi
from django.conf import settings


def get_connection_options():
    """
    Returns the options for connecting to Elasticsearch.
    """
    return {
        'verify_certs': True,
        'ca_certs': certifi.where(),
        'urls': settings.ES_URLS,
        'timeout': settings.ES_TIMEOUT,
    }

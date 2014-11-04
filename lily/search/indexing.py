import logging
import traceback

from django.conf import settings
from elasticutils.contrib.django import tasks


logger = logging.getLogger('search')


def update_in_index(instance, mapping):
    """
    Utility function for signal listeners index to Elasticsearch.
    Currently uses synchronous tasks. And because of that all exceptions are
    caught, so failures will not interfere with the regular model updates.
    """
    logger.info('Updating instance %s' % instance)
    if instance.is_deleted:
        try:
            tasks.unindex_objects(mapping, [instance.id], index=settings.ES_INDEXES['default'])
        except:
            pass
    else:
        try:
            tasks.index_objects(mapping, [instance.id], index=settings.ES_INDEXES['default'])
        except Exception, e:
            logger.error(traceback.format_exc(e))


def remove_from_index(instance, mapping):
    """
    Utility function for signal listeners to remove from Elasticsearch.
    Currently uses synchronous tasks. And because of that all exceptions are
    caught, so failures will not interfere with the regular model updates.
    """
    logger.info('Removing instance %s' % instance)
    try:
        tasks.unindex_objects(mapping, [instance.id], index=settings.ES_INDEXES['default'])
    except Exception, e:
        logger.error(traceback.format_exc(e))


def get_class(kls):
    '''
    Get a class by fully qualified class name.
    '''
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

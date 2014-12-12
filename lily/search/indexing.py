from datetime import date
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
    logger.info(u'Updating instance %s: %s' % (instance.__class__.__name__, instance.pk))
    if hasattr(instance, 'is_deleted') and instance.is_deleted:
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
    logger.info(u'Removing instance %s: %s' % (instance.__class__.__name__, instance.pk))
    try:
        tasks.unindex_objects(mapping, [instance.id], index=settings.ES_INDEXES['default'])
    except Exception, e:
        logger.error(traceback.format_exc(e))


def prepare_dict(arg_dict):
    """
    Cleans up a dict to be indexed. Returns a new dict.
    """

    # Remove entries with empty values.
    new_dict = {k: v for k, v in arg_dict.items() if v}

    for k, v in new_dict.iteritems():
        # Normalize dates.
        if type(v) is date:
            new_dict[k] = '%sT00:00:00.000000+00:00' % str(v)

        # Dedup lists.
        elif type(v) is list and len(v) > 1:
            new_dict[k] = list(set(v))

    return new_dict

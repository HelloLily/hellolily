from datetime import date
import itertools
import logging
import random
import time
import traceback

from django.conf import settings
from elasticsearch.exceptions import NotFoundError, ConnectionTimeout
from elasticutils.contrib.django import tasks, get_es

from lily.utils import logutil


logger = logging.getLogger('search')
NEW_INDEX = settings.ES_INDEXES['new_index']
DEFAULT_INDEX = settings.ES_INDEXES['default']
es = get_es()


def update_in_index(instance, mapping):
    """
    Utility function for signal listeners index to Elasticsearch.
    Currently uses synchronous tasks. And because of that all exceptions are
    caught, so failures will not interfere with the regular model updates.
    """
    if settings.ES_DISABLED:
        return
    if hasattr(instance, 'is_deleted') and instance.is_deleted:
        remove_from_index(instance, mapping)
    else:
        logger.info(u'Updating instance %s: %s' % (instance.__class__.__name__, instance.pk))
        # Extract all aliases available.
        aliases = list(itertools.chain(*[v['aliases'].keys() for v in es.indices.get_aliases().itervalues() if 'aliases' in v]))

        for index in [DEFAULT_INDEX, NEW_INDEX]:
            try:
                if index in aliases:
                    tasks.index_objects(mapping, [instance.id], index=index)
                    es.indices.refresh(index)
            except Exception, e:
                logger.error(traceback.format_exc(e))


def remove_from_index(instance, mapping):
    """
    Utility function for signal listeners to remove from Elasticsearch.
    Currently uses synchronous tasks. And because of that all exceptions are
    caught, so failures will not interfere with the regular model updates.
    """
    if settings.ES_DISABLED:
        return
    logger.info(u'Removing instance %s: %s' % (instance.__class__.__name__, instance.pk))
    # Extract all aliases available.
    aliases = list(itertools.chain(*[v['aliases'].keys() for v in es.indices.get_aliases().itervalues() if 'aliases' in v]))
    for index in [DEFAULT_INDEX, NEW_INDEX]:
        try:
            if index in aliases:
                tasks.unindex_objects(mapping, [instance.id], index=index)
                es.indices.refresh(index)
        except NotFoundError, e:
            logger.warn('Not found in index instance %s: %s' % (instance.__class__.__name__, instance.pk))
        except Exception, e:
            logger.error(traceback.format_exc(e))


def index_objects(mapping, queryset, index, print_progress=False):
    """
    Index synchronously model specified mapping type with an optimized query.
    """
    documents = []
    for instance in queryset_iterator(mapping, queryset, print_progress=print_progress):
        documents.append(mapping.extract_document(instance.id, instance))

        if len(documents) >= 100:
            for n in range(0, 6):
                try:
                    mapping.bulk_index(documents, id_field='id', index=index)
                    documents = []
                    break
                except ConnectionTimeout:
                    # After 6 tries, we should raise
                    if n == 5:
                        raise
                    sleep_time = (2 ** n) + random.randint(0, 1000) / 1000
                    logger.error('ConnectionTimeOut, sleeping for %s seconds' % sleep_time)
                    time.sleep(sleep_time)
                    pass

    for n in range(0, 6):
        try:
            mapping.bulk_index(documents, id_field='id', index=index)
            documents = []
            break
        except ConnectionTimeout:
            pass


def unindex_objects(mapping, queryset, index, print_progress=False):
    """
    Remove synchronously model specified mapping type with an optimized query.
    """
    queryset = queryset.only('pk')

    for instance in queryset_iterator(mapping, queryset, print_progress=print_progress):
        try:
            mapping.unindex(instance.pk, index=index)
        except NotFoundError:
            # Not present in the first place? Just ignore.
            pass


def queryset_iterator(mapping, queryset, chunksize=100, print_progress=False):
    """
    Returns an iterator that chops the queryset into chunks.

    This has several advantages over the standard iterator:

    - Supports prefetching.
    - Much faster because of batching.
    """

    queryset = mapping.prepare_batch(queryset)

    pk = 0
    progress = 0
    end = queryset.count()
    queryset = queryset.order_by('pk')
    while True:
        subset = queryset.filter(pk__gt=pk)[:chunksize]
        len_subset = len(subset)
        progress += len_subset
        if not len_subset:
            # Read all subsets until depleted.
            break
        if print_progress:
            logutil.print_progress(progress, end)
        for row in subset:
            pk = row.pk
            yield row


def prepare_dict(arg_dict):
    """
    Cleans up a dict to be indexed. Returns a new dict.
    """

    # Remove entries with empty values.
    new_dict = {k: v for k, v in arg_dict.items() if v not in ([], '', {}, None)}

    for k, v in new_dict.iteritems():
        # Normalize dates.
        if type(v) is date:
            new_dict[k] = '%sT00:00:00.000000+00:00' % str(v)

        # Dedup lists.
        elif type(v) is list and len(v) > 1 and type(v[0]) is not dict:
            new_dict[k] = list(set(v))

    return new_dict

from datetime import date
import logging
import traceback

from django.conf import settings
from elasticsearch.exceptions import NotFoundError
from elasticutils.contrib.django import tasks

from lily.utils import logutil


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


def index_objects(mapping, queryset, index, print_progress=False):
    """
    Index synchronously model specified mapping type with an optimized query.
    """
    documents = []
    for instance in queryset_iterator(mapping, queryset, print_progress=print_progress):
        documents.append(mapping.extract_document(instance.id, instance))

        if len(documents) >= 100:
            mapping.bulk_index(documents, id_field='id', index=index)
            documents = []

    mapping.bulk_index(documents, id_field='id', index=index)


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
        elif type(v) is list and len(v) > 1:
            new_dict[k] = list(set(v))

    return new_dict

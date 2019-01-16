from datetime import date
import logging
import traceback

from django.conf import settings
from elasticsearch_old.exceptions import NotFoundError
from elasticutils.contrib.django import tasks

from lily.search.connections_utils import get_es_client, get_index_name
from lily.utils import logutil


logger = logging.getLogger('search')
main_index = settings.ES_OLD_INDEXES['default']
es = get_es_client(maxsize=1)


def update_in_index(instance, mapping):
    """
    Utility function for signal listeners index to Elasticsearch.
    Currently uses synchronous tasks. And because of that all exceptions are
    caught, so failures will not interfere with the regular model updates.
    """
    if settings.ES_OLD_DISABLED:
        return
    if hasattr(instance, 'is_deleted') and instance.is_deleted:
        remove_from_index(instance, mapping)
    else:
        logger.info(u'Updating instance %s: %s' % (instance.__class__.__name__, instance.pk))

        try:
            main_index_with_type = get_index_name(main_index, mapping)
            try:
                document = mapping.extract_document(instance.id, instance)
            except Exception as exc:
                logger.exception('Unable to extract document {0}: {1}'.format(
                    instance, repr(exc)))
            else:
                # Index object direct instead of bulk_index, to prevent multiple reads from db
                mapping.index(document, id_=instance.id, es=es, index=main_index_with_type)
                es.indices.refresh(main_index_with_type)
        except Exception, e:
            logger.error(traceback.format_exc(e))


def remove_from_index(instance, mapping):
    """
    Utility function for signal listeners to remove from Elasticsearch.
    Currently uses synchronous tasks. And because of that all exceptions are
    caught, so failures will not interfere with the regular model updates.
    """
    if settings.ES_OLD_DISABLED:
        return
    logger.info(u'Removing instance %s: %s' % (instance.__class__.__name__, instance.pk))

    try:
        main_index_with_type = get_index_name(main_index, mapping)
        tasks.unindex_objects(mapping, [instance.id], es=es, index=main_index_with_type)
        es.indices.refresh(main_index_with_type)
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
            mapping.bulk_index(documents, id_field='id', index=get_index_name(index, mapping), es=es)
            documents = []

    mapping.bulk_index(documents, id_field='id', index=get_index_name(index, mapping), es=es)
    documents = []


def unindex_objects(mapping, queryset, index, print_progress=False):
    """
    Remove synchronously model specified mapping type with an optimized query.
    """
    queryset = queryset.only('pk')

    for instance in queryset_iterator(mapping, queryset, print_progress=print_progress):
        try:
            mapping.unindex(instance.pk, index=get_index_name(index, mapping), es=es)
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

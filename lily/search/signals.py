from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from lily.search.indexing import get_class, update_in_index, remove_from_index


CLASS_MAPPINGS = [get_class(kls) for kls in settings.ES_MODEL_MAPPINGS]
CLASS_MODELS = [mapping.get_model() for mapping in CLASS_MAPPINGS]


@receiver(post_save)
def update_in_index_generic(sender, instance, **kwargs):
    if sender in CLASS_MODELS:
        index = CLASS_MODELS.index(sender)
        mapping = CLASS_MAPPINGS[index]
        update_in_index(instance, mapping)


@receiver(post_delete)
def remove_from_index_generic(sender, instance, **kwargs):
    if sender in CLASS_MODELS:
        index = CLASS_MODELS.index(sender)
        mapping = CLASS_MAPPINGS[index]
        remove_from_index(instance, mapping)

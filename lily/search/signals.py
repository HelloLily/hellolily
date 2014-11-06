import itertools

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from lily.search.indexing import get_class, update_in_index, remove_from_index


CLASS_MAPPINGS = [get_class(kls) for kls in settings.ES_MODEL_MAPPINGS]
MODEL_TO_MAPPING = {kls.get_model(): kls for kls in CLASS_MAPPINGS}
RELATED = set(itertools.chain(*[kls.get_related_models() for kls in CLASS_MAPPINGS]))


@receiver(post_save)
def post_save_generic(sender, instance, **kwargs):
    mapping = MODEL_TO_MAPPING.get(sender)
    if mapping:
        update_in_index(instance, mapping)
    # Check for related model signals.
    if sender in RELATED:
        for field_name in [field.name for field in sender._meta.concrete_fields]:
            mapping = MODEL_TO_MAPPING.get(getattr(instance, field_name).__class__)
            if mapping:
                if sender in mapping.get_related_models():
                    update_in_index(getattr(instance, field_name), mapping)


@receiver(post_delete)
def post_delete_generic(sender, instance, **kwargs):
    mapping = MODEL_TO_MAPPING.get(sender)
    if mapping:
        remove_from_index(instance, mapping)

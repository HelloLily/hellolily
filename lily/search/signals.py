from django.conf import settings
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch.dispatcher import receiver

from lily.search.indexing import get_class, update_in_index, remove_from_index


CLASS_MAPPINGS = [get_class(kls) for kls in settings.ES_MODEL_MAPPINGS]
MODEL_TO_MAPPING = {kls.get_model(): kls for kls in CLASS_MAPPINGS}


@receiver(post_save)
def post_save_generic(sender, instance, **kwargs):
    mapping = MODEL_TO_MAPPING.get(sender)
    if mapping:
        update_in_index(instance, mapping)
    check_related(sender, instance)


@receiver(m2m_changed)
def m2m_changed_generic(sender, instance, action, **kwargs):
    if action.startswith('post_'):
        mapping = MODEL_TO_MAPPING.get(type(instance))
        if mapping:
            update_in_index(instance, mapping)
        check_related(sender, instance)


@receiver(post_delete)
def post_delete_generic(sender, instance, **kwargs):
    mapping = MODEL_TO_MAPPING.get(sender)
    if mapping:
        remove_from_index(instance, mapping)
    # Remember: We UPDATE our related object, not DELETE it
    # (So we can use the check_related also used in the post_save method).
    check_related(sender, instance)


def check_related(sender, instance):
    """
    Check related models by checking if the sender is in the relations of the
    mappings.
    """
    for mapping in MODEL_TO_MAPPING.values():
        # Use type(instance) because of sender, because m2m sender differs
        # from type(instance).
        related = mapping.get_related_models().get(type(instance))
        if related:
            for obj in related(instance):
                update_in_index(obj, mapping)

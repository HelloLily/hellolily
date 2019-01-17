from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch.dispatcher import receiver

from .indexing import update_in_index, remove_from_index
from .scan_search import ModelMappings
from django.conf import settings

from functools import wraps


def skip_signal():
    def _skip_signal(signal_func):
        @wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, 'skip_signal') and instance.skip_signal:
                return None
            return signal_func(sender, instance, **kwargs)
        return _decorator
    return _skip_signal


@receiver(post_save)
@skip_signal()
def post_save_generic(sender, instance, **kwargs):
    if settings.ES_OLD_DISABLED:
        return
    mapping = ModelMappings.model_to_mappings.get(sender)
    if mapping:
        update_in_index(instance, mapping)
    check_related(sender, instance)


@receiver(m2m_changed)
@skip_signal()
def m2m_changed_generic(sender, instance, action, **kwargs):
    if settings.ES_OLD_DISABLED:
        return
    if action.startswith('post_'):
        mapping = ModelMappings.model_to_mappings.get(type(instance))
        if mapping:
            update_in_index(instance, mapping)
        check_related(sender, instance)


@receiver(post_delete)
def post_delete_generic(sender, instance, **kwargs):
    if settings.ES_OLD_DISABLED:
        return
    mapping = ModelMappings.model_to_mappings.get(sender)
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
    for mapping in ModelMappings.mappings:
        # Use type(instance) because of sender, because m2m sender differs
        # from type(instance).
        related = mapping.get_related_models().get(type(instance))
        if related:
            for obj in related(instance):
                # Some related objects are not specific to one model, such as
                # 'subject' of Tag, so we do a double check to match the model.
                if type(obj) is mapping.get_model():
                    update_in_index(obj, mapping)

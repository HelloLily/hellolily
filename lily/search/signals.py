from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch.dispatcher import receiver

from .indexing import update_in_index, remove_from_index
from .scan_search import ModelMappings


@receiver(post_save)
def post_save_generic(sender, instance, **kwargs):
    mapping = ModelMappings.get_model_mappings().get(sender)
    if mapping:
        update_in_index(instance, mapping)
    check_related(sender, instance)


@receiver(m2m_changed)
def m2m_changed_generic(sender, instance, action, **kwargs):
    if action.startswith('post_'):
        mapping = ModelMappings.get_model_mappings().get(type(instance))
        if mapping:
            update_in_index(instance, mapping)
        check_related(sender, instance)


@receiver(post_delete)
def post_delete_generic(sender, instance, **kwargs):
    mapping = ModelMappings.get_model_mappings().get(sender)
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
    for mapping in ModelMappings.get_model_mappings().values():
        # Use type(instance) because of sender, because m2m sender differs
        # from type(instance).
        related = mapping.get_related_models().get(type(instance))
        if related:
            for obj in related(instance):
                # Some related objects are not specific to one model, such as
                # 'subject' of Tag, so we do a double check to match the model.
                if type(obj) is mapping.get_model():
                    update_in_index(obj, mapping)
